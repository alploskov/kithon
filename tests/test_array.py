from utils import check_func, check_exprs


def list_res(data, lang):
    if lang == 'lua':
        return list(data.values())
    return data

def test_defenition():
    exprs = [
        '[]',
        '[1]',
        '[1,2,3,4]',
    ]
    check_exprs(exprs, list_res)


def index():
    arr = [1,2,3,4]
    return [arr[0], arr[1], arr[-1], arr[2]]

def test_index():
    check_func(index, list_res)

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
#    arr[:10]
        arr[::1],
        arr[::-1],
        arr[1:-1:2],
        arr[-1:1:-1],
        arr[-1:1:-2],
        arr[::b],
    ]

def test_slices():
    def post_process(d, l):
        if l != 'lua':
            return d
        print(d)
        return [list(_d.values()) for _d in d.values()]
    check_func(slices, post_process)
