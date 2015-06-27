import json


class Chart(object):
    def __init__(self, id=None, kind=None, options=None, columns=None, rows=None):
        '''
        id -- div's id
        options -- whatever Google Charts accepts
        columns -- list of (type, name)
        '''
        self.id = id
        self.kind = kind
        self.options = options
        self.columns = columns
        self.rows = rows
        if not options:
            self.options = {}
        if not columns:
            self.columns = []
        if not self.rows:
            self.rows = []

    @property
    def typeof(self):
        return self.__class__.__name__

    @property
    def rows_json(self):
        return json.dumps(self.rows)

    @property
    def options_json(self):
        return json.dumps(self.options)
