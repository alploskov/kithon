from utils import check_func, check_exprs, type_conversion


def test_defenition():
    exprs = [
        '[]',
        '[1]',
        '[1,2,3,4]',
        '[[]]',
        '[[1]]',
        '[[1],[2]]',
    ]
    check_exprs(exprs)


def index():
    arr = [1,2,3,4]
    return [arr[0], arr[1], arr[-1], arr[2]]

def test_index():
    check_func(index)

def test_lens():
    exprs = [
        'len([])',
        'len([1])',
        'len([1,2,3,4])',
    ]
    check_exprs(exprs)
    
def slices():
    arr = [1, 2, 3, 4, 5, 6]
    b = 2
    return [
        arr[:],
        arr[0:],
        arr[1:],
        arr[:-1],
        arr[0:-1],
        arr[1:-1],
        arr[-1:1],
        arr[:10],
        arr[::1],
        arr[::-1],
        arr[1:-1:2],
        arr[-1:1:-1],
        arr[-1:1:-2],
        arr[::b],
    ]

def test_slices():
    check_func(slices)

def assignment():
    arr = [1, 2, 3, 4]
    i1 = 1
    arr[0] = 100
    arr[i1] = 200
    arr[-2] = 300
    i2 = -1
    arr[i2] = 400
    return arr

def test_assignment():
    check_func(assignment)
