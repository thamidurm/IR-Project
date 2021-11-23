class Filter:

    def __init__(self, entity, operator, value, position):
        self.entity = entity
        self.operator = operator
        self.value = value
        self.position = position

    def __repr__(self):
        return 'entity: {0}, operator: {1}, value: {2}, idx: {3}'.format(self.entity, self.operator, self.value, self.position)
