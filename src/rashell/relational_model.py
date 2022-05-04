class Relation:
    def __init__(self, parent, name, attributes, foreign_keys):
        self.parent = parent
        self.name = name
        self.attributes = attributes
        self.foreign_keys = foreign_keys
        self.tuples = set()
        self.is_temporary = False


class Attribute:
    def __init__(self, parent, is_primary_key, is_foreign_key, name):
        self.parent = parent
        self.is_primary_key = is_primary_key
        self.is_foreign_key = is_foreign_key
        self.name = name
