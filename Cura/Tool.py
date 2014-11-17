class Tool(object):
    def __init__(self):
        super(Tool, self).__init__() # Call super to make multiple inheritence work.
        self._renderer = None