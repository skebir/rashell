class RashellException(Exception):
    pass


class DuplicateRelationDefinitionException(RashellException):
    def __init__(self, relations, line):
        super().__init__('Line {}: Duplicate definitions of the same relations {}'.format(line, relations))


class RelationAlreadyExistsException(RashellException):
    def __init__(self, name, line):
        super().__init__('Line {}: Relation {} already exists'.format(line, name))


class DuplicateAttributesException(RashellException):
    def __init__(self, duplicate_attributes, line):
        super().__init__('Line {}: Duplicate attributes {}'.format(line, duplicate_attributes))


class PrimaryKeyAttributesNotDefinedException(RashellException):
    def __init__(self, not_defined_attributes, line):
        super().__init__('Line {}: Primary key attributes {} not defined in attributes list'.format(
            line,
            not_defined_attributes,
        ))


class ForeignKeyNotExplainedException(RashellException):
    def __init__(self, attributes, line):
        super().__init__('Line {}: Foreign key attributes {} not explained'.format(
            line,
            attributes,
        ))


class ForeignKeyNotDefinedException(RashellException):
    def __init__(self, attributes, line):
        super().__init__('Line {}: Foreign key attributes {} explained but not defined'.format(
            line,
            attributes,
        ))


class RelationNotFoundException(RashellException):
    def __init__(self, name, line):
        super().__init__('Line {}: Relation {} not found'.format(
            line,
            name,
        ))


class ReferencedRelationNotDefinedException(RashellException):
    def __init__(self, relation, line):
        super().__init__('Line {}: Referenced relation {} not defined'.format(
            line,
            relation,
        ))


class ReferencedAttributenNotDefinedException(RashellException):
    def __init__(self, relation, attribute, line):
        super().__init__('Line {}: Referenced attribute {}.{} not defined'.format(
            line,
            relation,
            attribute
        ))


class TupleArityDifferentFromRelationArityException(RashellException):
    def __init__(self, tuple_arity, number_of_attributes, line):
        super().__init__('Line {}: Arity of tuple is {}. Expected {}'.format(
            line,
            tuple_arity,
            number_of_attributes
        ))


class PrimaryKeyConstraintFailed(RashellException):
    def __init__(self, pk_tuple, line):
        super().__init__('Line {}: Primary Key constraint failed {}'.format(line, pk_tuple))


class ForeignKeyConstaintFailedException(RashellException):
    def __init__(self, fk_tuple, line):
        super().__init__('Line {}: Foreign Key constraint failed {}'.format(line, fk_tuple))


class ProjectionColumnsNotDefinedException(RashellException):
    def __init__(self, relation, projection_columns, line):
        super().__init__(
            'Line {}: Projection columns {} not defined in relation {}'.format(line, projection_columns, relation))


class RestrictionColumnNotDefinedException(RashellException):
    def __init__(self, relation, restriction_column, line):
        super().__init__(
            'Line {}: Restriction column {} not defined in relation {}'.format(line, restriction_column, relation))


class JoinColumnNotDefinedException(RashellException):
    def __init__(self, relation, join_column, line):
        super().__init__('Line {}: Join column {} not defined in relation {}'.format(line, join_column, relation))


class UnionRelationsHavingDifferentNumberOfAttribute(RashellException):
    def __init__(self, left_r, right_r, line):
        super().__init__('Line {}: Union relations {}, {} have different attributes'.format(line, left_r, right_r))


class RestrictionRelationsHavingDifferentNumberOfAttribute(RashellException):
    def __init__(self, left_r, right_r, line):
        super().__init__(
            'Line {}: Restriction relations {}, {} have different attributes'.format(line, left_r, right_r))


class DifferenceRelationsHavingDifferentNumberOfAttribute(RashellException):
    def __init__(self, left_r, right_r, line):
        super().__init__('Line {}: Difference relations {}, {} have different attributes'.format(line, left_r, right_r))


class DeleteColumnNotDefinedException(Exception):
    def __init__(self, relation, restriction_column, line):
        super().__init__(
            'Line {}: Delete column {} not defined in relation {}'.format(line, restriction_column, relation))
