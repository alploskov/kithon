from collections import namedtuple


Loop = namedtuple(
    'Loop',
    [
        'name', # while/for
        'els'   # does the loop have a else block
    ]
)

Try = namedtuple('Try', ['name'])
