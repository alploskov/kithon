from utils import check_exprs


def test_convert():
    exprs = [
        'int("10")',
        'int("10", 2)',
        'float("10.2")',
    ]
    check_exprs(exprs)

def test_op():
    exprs = [
        '10 - 5',
        '6 * 8',
        '2+2*2',
        '2 ** 2',
        '3 ** 3',
        '0 ** 0',
        '1 ** 0',
        '2 ** 1',
    ]
    check_exprs(exprs)

