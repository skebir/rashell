import os
import sys

from rich import box, print
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textx import metamodel_from_file, textx_isinstance, get_location

from rashell.exceptions import DuplicateRelationDefinitionException, DuplicateAttributesException, \
    ForeignKeyNotExplainedException, ForeignKeyNotDefinedException, ReferencedRelationNotDefinedException, \
    ReferencedAttributenNotDefinedException, RelationNotFoundException, TupleArityDifferentFromRelationArityException, \
    PrimaryKeyConstraintFailed, ForeignKeyConstaintFailedException, ProjectionColumnsNotDefinedException, \
    RestrictionColumnNotDefinedException, JoinColumnNotDefinedException, UnionRelationsHavingDifferentNumberOfAttribute, \
    RestrictionRelationsHavingDifferentNumberOfAttribute, DifferenceRelationsHavingDifferentNumberOfAttribute, \
    RelationAlreadyExistsException, DeleteColumnNotDefinedException
from rashell.relational_model import Relation, Attribute


class RelationalEngine:
    def __init__(self):
        self.relations = set()
        self.instruction_mm = metamodel_from_file(os.path.join(os.path.dirname(__file__),
                                                               'grammar_files/rashell_grammar.tx'),
                                                  classes=[Relation])
        self.instruction_mm.register_obj_processors({
            'PartialRelationalModel': self.process_partial_relational_model,
            'Insert': self.process_insert,
            'PrintRelation': self.print_relation,
            'PrintModel': self.print_model,
            'Operation': self.process_operation,
            'Delete': self.process_delete,
            'Exit': self.process_exit
        })

    def process_exit(self, exit):
        sys.exit('Goodbye!')

    def process_delete(self, delete):
        line = get_location(delete)['line']
        r = self.get_relation_by_name(delete.relation_name)
        if not r:
            raise RelationNotFoundException(delete.relation_name, line)

        if delete.condition.attribute_name not in {a.name for a in r.attributes}:
            raise DeleteColumnNotDefinedException(delete.relation_name,
                                                  delete.condition.attribute_name, line)

        for a in r.attributes:
            if a.name == delete.condition.attribute_name:
                break
        index = r.attributes.index(a)

        tuples_to_delete = {t for t in r.tuples if
                            self.eval_condition(t[index], delete.condition.operator, delete.condition.value)}

        if delete.delete_type == 'delete':
            referencer_relations = {referencer_relation for referencer_relation in self.relations if
                                    {fk for fk in referencer_relation.foreign_keys if
                                     fk.referenced_relation_name == delete.relation_name}}
            for referencer_relation in referencer_relations:
                for fk in referencer_relation.foreign_keys:
                    if fk.referenced_relation_name == delete.relation_name:
                        for a in r.attributes:
                            if a.name == fk.referenced_attribute_name:
                                break
                        referenced_attribute_index = r.attributes.index(a)
                        referenced_attribute_values = {t[referenced_attribute_index] for t in tuples_to_delete}

                        for a in referencer_relation.attributes:
                            if a.name == fk.referencer_attribute_name:
                                break
                        referencer_attribute_index = referencer_relation.attributes.index(a)
                        referencer_attribute_values = {t[referencer_attribute_index] for t in
                                                       referencer_relation.tuples}
                        intersection = referenced_attribute_values.intersection(referencer_attribute_values)
                        if intersection:
                            raise ForeignKeyConstaintFailedException(intersection, line)

        r.tuples.difference_update(tuples_to_delete)

    def open_from_file(self, file_name):
        self.program_mm = metamodel_from_file(os.path.join(os.path.dirname(__file__),
                                                           'grammar_files/rashell_program_grammar.tx'),
                                              classes=[Relation])
        program = self.program_mm.model_from_file(file_name)
        self.process_partial_relational_model(program.partial_relational_model)
        for command in program.commands:
            if textx_isinstance(command, self.instruction_mm['Assignment']):
                self.process_assignment(command)
            elif textx_isinstance(command, self.instruction_mm['Insert']):
                self.process_insert(command)

    def process_assignment(self, assignment):
        line = get_location(assignment)['line']
        existing_relation = self.get_relation_by_name(assignment.result_name)
        if existing_relation and not existing_relation.is_temporary:
            raise RelationAlreadyExistsException(assignment.result_name, line)
        else:
            temp_relation = self.compute_relational_algebra_operation(assignment.relational_algebra_operation)
            if existing_relation:
                existing_relation.attributes = temp_relation.attributes
                existing_relation.tuples = temp_relation.tuples
            else:
                temp_relation.name = assignment.result_name
                temp_relation.foreign_keys = []
                temp_relation.is_temporary = True
                self.relations.add(temp_relation)

    def process_operation(self, operation):
        if textx_isinstance(operation.operation_type, self.instruction_mm['Assignment']):
            self.process_assignment(operation.operation_type)
        elif textx_isinstance(operation.operation_type, self.instruction_mm['RelationalAlgebraOperation']):
            temp_relation = self.compute_relational_algebra_operation(operation.operation_type)
            self.print_table(temp_relation)

    def compute_relational_algebra_operation(self, operation):
        if textx_isinstance(operation, self.instruction_mm['Projection']):
            temp_relation = self.compute_projection(operation)
        elif textx_isinstance(operation, self.instruction_mm['Restriction']):
            temp_relation = self.compute_restriction(operation)
        elif textx_isinstance(operation, self.instruction_mm['Join']):
            temp_relation = self.compute_join(operation)
        elif textx_isinstance(operation, self.instruction_mm['Union']):
            temp_relation = self.compute_union(operation)
        elif textx_isinstance(operation, self.instruction_mm['Intersection']):
            temp_relation = self.compute_intersection(operation)
        elif textx_isinstance(operation, self.instruction_mm['Difference']):
            temp_relation = self.compute_difference(operation)
        elif textx_isinstance(operation, self.instruction_mm['CartesianProduct']):
            temp_relation = self.compute_cartesian_product(operation)
        return temp_relation

    def process_partial_relational_model(self, partial_relational_model):
        line = get_location(partial_relational_model)['line']
        relations_names = [r.name for r in partial_relational_model.relations]
        if len(set(relations_names)) != len(relations_names):
            seen = set()
            duplicate_relations = [x for x in relations_names if x in seen or seen.add(x)]
            raise DuplicateRelationDefinitionException(duplicate_relations, line)
        intersection = set(relations_names).intersection({r.name for r in self.relations})
        if intersection:
            raise DuplicateRelationDefinitionException(intersection, line)
        for relation in partial_relational_model.relations:
            attributes_names = [a.name for a in relation.attributes]
            if len(set(attributes_names)) != len(attributes_names):
                seen = set()
                duplicate_attributes = [x for x in attributes_names if x in seen or seen.add(x)]
                raise DuplicateAttributesException(duplicate_attributes, line)
            fk_attributes_names = {a.name for a in relation.attributes if a.is_foreign_key}
            referencer_attributes_names = {fk.referencer_attribute_name for fk in relation.foreign_keys}
            fk_not_explained = fk_attributes_names - referencer_attributes_names
            referencer_not_defined = referencer_attributes_names - fk_attributes_names
            if fk_not_explained:
                raise ForeignKeyNotExplainedException(fk_not_explained, line)
            if referencer_not_defined:
                raise ForeignKeyNotDefinedException(referencer_not_defined, line)
            for foreign_key in relation.foreign_keys:
                if foreign_key.referenced_relation_name not in relations_names and foreign_key.referenced_relation_name not in {
                    r.name for r in self.relations}:
                    raise ReferencedRelationNotDefinedException(foreign_key.referenced_relation_name, line)
                found = False
                for relation in partial_relational_model.relations:
                    if relation.name == foreign_key.referenced_relation_name:
                        found = True
                        break
                if not found:
                    for relation in self.relations:
                        if relation.name == foreign_key.referenced_relation_name:
                            break
                if foreign_key.referenced_attribute_name not in [a.name for a in relation.attributes]:
                    raise ReferencedAttributenNotDefinedException(relation.name, foreign_key.referenced_attribute_name,
                                                                  line)

        self.relations.update(partial_relational_model.relations)

    def get_relation_by_name(self, name):
        return next((r for r in self.relations if r.name == name), None)

    @staticmethod
    def print_table(relation):
        table = Table(box=box.HORIZONTALS, highlight=False)
        for a in [attribute.name for attribute in relation.attributes]:
            table.add_column(a, justify="center")
        for t in relation.tuples:
            table.add_row(*(str(cell) for cell in t))
        print(table)

    def process_insert(self, insert):
        line = get_location(insert)['line']
        r = self.get_relation_by_name(insert.relation_name)
        if not r:
            raise RelationNotFoundException(insert.relation_name, line)

        if len(insert.values) != len(r.attributes):
            raise TupleArityDifferentFromRelationArityException(len(insert.values), len(r.attributes), line)

        pk_indexes = {index for index, a in enumerate(r.attributes) if a.is_primary_key}
        pk_tuples = {tuple(t[pk_index] for pk_index in pk_indexes) for t in r.tuples}
        pk_tuple = tuple(insert.values[pk_index] for pk_index in pk_indexes)
        if pk_indexes and pk_tuple in pk_tuples:
            raise PrimaryKeyConstraintFailed(pk_tuple, line)
        if insert.insert_type == 'insert':
            for referencer_attribute_name, referenced_relation_name, referenced_attribute_name in [
                (fk.referencer_attribute_name, fk.referenced_relation_name,
                 fk.referenced_attribute_name) for fk in r.foreign_keys]:
                for a in r.attributes:
                    if a.name == referencer_attribute_name:
                        break
                referencer_attribute_index = r.attributes.index(a)
                referencer_attribute_value = insert.values[referencer_attribute_index]
                referenced_relation = self.get_relation_by_name(referenced_relation_name)
                for a in referenced_relation.attributes:
                    if a.name == referenced_attribute_name:
                        break
                referenced_attribute_index = referenced_relation.attributes.index(a)
                referenced_attribute_values = {t[referenced_attribute_index] for t in referenced_relation.tuples}
                if referencer_attribute_value not in referenced_attribute_values:
                    raise ForeignKeyConstaintFailedException(referencer_attribute_value, line)

        user_tuple = tuple(insert.values)
        r.tuples.add(user_tuple)

    def print_relation(self, print_relation):
        line = get_location(print_relation)['line']
        r = self.get_relation_by_name(print_relation.relation_name)
        if not r:
            raise RelationNotFoundException(print_relation.relation_name, line)

        self.print_table(r)

    def print_model(self, model_type):
        if model_type == '.raw_model':
            model_string = Text('\n'.join([
                '{}({}){}'.format(
                    r.name,
                    ', '.join(f'{"_" if a.is_primary_key else ""}{"#" if a.is_foreign_key else ""}{a.name}' for a in
                              r.attributes),
                    '{}{}'.format(
                        '\n' if r.foreign_keys else "",
                        '\n'.join(['    {} references {}.{}'.format(
                            fk.referencer_attribute_name,
                            fk.referenced_relation_name,
                            fk.referenced_attribute_name
                        ) for fk in r.foreign_keys])
                    )
                ) for r in
                [first_r for first_r in self.relations if not first_r.is_temporary] + [second_r for second_r in
                                                                                       self.relations if
                                                                                       second_r.is_temporary]]
            ))
        else:
            model_string = Panel('\n'.join([
                '{}[b]{}[/]({}){}{}'.format(
                    '[dim]' if r.is_temporary else '',
                    r.name,
                    ', '.join('{}{}{}{}{}{}'.format(
                        '[u]' if a.is_primary_key else '',
                        '#' if a.is_foreign_key else '',
                        '[i]' if a.is_foreign_key else '',
                        a.name,
                        '[/]' if a.is_foreign_key else '',
                        '[/]' if a.is_primary_key else ''
                    ) for a in r.attributes),
                    '{}{}'.format(
                        '\n' if r.foreign_keys else "",
                        '\n'.join(['    [i]{}[/] references {}.{}'.format(
                            fk.referencer_attribute_name,
                            fk.referenced_relation_name,
                            fk.referenced_attribute_name
                        ) for fk in r.foreign_keys])
                    ),
                    '[/]' if r.is_temporary else ''
                ) for r in
                [first_r for first_r in self.relations if not first_r.is_temporary] + [second_r for second_r in
                                                                                       self.relations if
                                                                                       second_r.is_temporary]]
            ), expand=False)
        print(model_string)

    def compute_projection(self, projection):
        line = get_location(projection)['line']
        r = self.get_relation_by_name(projection.relation_name)
        if not r:
            raise RelationNotFoundException(projection.relation_name, line)

        unfound_projection_columns = set(projection.columns) - {a.name for a in r.attributes}
        if unfound_projection_columns:
            raise ProjectionColumnsNotDefinedException(projection.relation_name, unfound_projection_columns, line)

        temp_relation = Relation(None, None, [Attribute(None, False, False, c) for c in projection.columns], None)

        projection_indexes = {index for index, a in enumerate(r.attributes) if a.name in projection.columns}
        temp_relation.tuples = {tuple(t[projection_index] for projection_index in projection_indexes) for t in r.tuples}

        return temp_relation

    @staticmethod
    def eval_condition(a, op, b):
        if op == '=':
            return a == b
        elif op == '>':
            return a > b
        elif op == '>=':
            return a >= b
        elif op == '<=':
            return a <= b
        elif op == '<':
            return a < b
        elif op == '!=' or '<>':
            return a != b

    def compute_restriction(self, restriction):
        line = get_location(restriction)['line']

        r = self.get_relation_by_name(restriction.relation_name)
        if not r:
            raise RelationNotFoundException(restriction.relation_name, line)

        # check if condition column in relation.attributes
        if restriction.condition.attribute_name not in {a.name for a in r.attributes}:
            raise RestrictionColumnNotDefinedException(restriction.relation_name, restriction.condition.attribute_name,
                                                       line)

        temp_relation = Relation(None, None, [Attribute(None, None, None, a.name) for a in r.attributes], None)

        for a in r.attributes:
            if a.name == restriction.condition.attribute_name:
                break
        index = r.attributes.index(a)

        temp_relation.tuples = {t for t in r.tuples if
                                self.eval_condition(t[index], restriction.condition.operator,
                                                    restriction.condition.value)}
        return temp_relation

    def compute_join(self, join):
        line = get_location(join)['line']
        left_r = self.get_relation_by_name(join.left_relation)
        right_r = self.get_relation_by_name(join.right_relation)
        if not left_r:
            raise RelationNotFoundException(join.left_relation, line)
        if not right_r:
            raise RelationNotFoundException(join.right_relation, line)

        if join.condition.left_attribute not in {a.name for a in left_r.attributes}:
            raise JoinColumnNotDefinedException(join.left_relation, join.condition.left_attribute, line)
        if join.condition.right_attribute not in {a.name for a in right_r.attributes}:
            raise JoinColumnNotDefinedException(join.right_relation, join.condition.right_attribute, line)

        temp_relation = Relation(None, None, [Attribute(None, None, None, a.name) for a in left_r.attributes] + [
            Attribute(None, None, None,
                      f'{a.name}{"_" if a.name in [left_a.name for left_a in left_r.attributes] else ""}') for a in
            right_r.attributes], None)

        for left_attribute in left_r.attributes:
            if left_attribute.name == join.condition.left_attribute:
                break
        left_index = left_r.attributes.index(left_attribute)

        for right_attribute in right_r.attributes:
            if right_attribute.name == join.condition.right_attribute:
                break
        right_index = right_r.attributes.index(right_attribute)

        temp_relation.tuples = {
            l_tuple + r_tuple for l_tuple in left_r.tuples for r_tuple in right_r.tuples if
            l_tuple[left_index] == r_tuple[right_index]
        }

        return temp_relation

    def compute_union(self, union):
        line = get_location(union)['line']
        left_r = self.get_relation_by_name(union.left_relation)
        right_r = self.get_relation_by_name(union.right_relation)
        if not left_r:
            raise RelationNotFoundException(union.left_relation, line)
        if not right_r:
            raise RelationNotFoundException(union.right_relation, line)

        if len(left_r.attributes) != len(right_r.attributes):
            raise UnionRelationsHavingDifferentNumberOfAttribute(union.left_relation, union.right_relation, line)

        temp_relation = Relation(None, None, [Attribute(None, None, None, a.name) for a in left_r.attributes], None)

        temp_relation.tuples = left_r.tuples.union(right_r.tuples)
        return temp_relation

    def compute_intersection(self, intersection):
        line = get_location(intersection)
        left_r = self.get_relation_by_name(intersection.left_relation)
        right_r = self.get_relation_by_name(intersection.right_relation)
        if not left_r:
            raise RelationNotFoundException(intersection.left_relation, line)
        if not right_r:
            raise RelationNotFoundException(intersection.right_relation, line)

        if len(left_r.attributes) != len(right_r.attributes):
            raise RestrictionRelationsHavingDifferentNumberOfAttribute(intersection.left_relation,
                                                                       intersection.right_relation,
                                                                       line)

        temp_relation = Relation(None, None, [Attribute(None, None, None, a.name) for a in left_r.attributes], None)

        temp_relation.tuples = left_r.tuples.intersection(right_r.tuples)
        return temp_relation

    def compute_difference(self, difference):
        line = get_location(difference)['line']
        left_r = self.get_relation_by_name(difference.left_relation)
        right_r = self.get_relation_by_name(difference.right_relation)
        if not left_r:
            raise RelationNotFoundException(difference.left_relation, line)
        if not right_r:
            raise RelationNotFoundException(difference.right_relation, line)

        if len(left_r.attributes) != len(right_r.attributes):
            raise DifferenceRelationsHavingDifferentNumberOfAttribute(difference.left_relation,
                                                                      difference.right_relation,
                                                                      line)

        temp_relation = Relation(None, None, [Attribute(None, None, None, a.name) for a in left_r.attributes], None)

        temp_relation.tuples = left_r.tuples.difference(right_r.tuples)
        return temp_relation

    def compute_cartesian_product(self, cartesian_product):
        line = get_location(cartesian_product)['line']
        left_r = self.get_relation_by_name(cartesian_product.left_relation)
        right_r = self.get_relation_by_name(cartesian_product.right_relation)
        if not left_r:
            raise RelationNotFoundException(cartesian_product.left_relation, line)
        if not right_r:
            raise RelationNotFoundException(cartesian_product.right_relation, line)

        temp_relation = Relation(None, None, [Attribute(None, None, None, a.name) for a in left_r.attributes] + [
            Attribute(None, None, None,
                      f'{a.name}{"_" if a.name in [left_a.name for left_a in left_r.attributes] else ""}') for a in
            right_r.attributes], None)

        temp_relation.tuples = {
            l_tuple + r_tuple for l_tuple in left_r.tuples for r_tuple in right_r.tuples
        }
        return temp_relation
