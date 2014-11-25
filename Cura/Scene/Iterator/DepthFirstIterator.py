from . import Iterator

class DepthFirstIterator(Iterator.Iterator):
    def __init__(self):
        super(DepthFirstIterator, self).__init__() # Call super to make multiple inheritence work.