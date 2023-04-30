from collections import namedtuple


Loop = namedtuple(
    'Loop',
    [
        'name', # while/for
        'els',   # does the loop have a else block
        'is_continuing',
        'is_broken',
    ],
    defaults=('', False, False, False)
)

Try = namedtuple('Try', ['name'])
