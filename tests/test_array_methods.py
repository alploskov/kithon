from utils import check_func


def append():
    arr = []
    arr.append(1)
    return arr

def extend():
    arr = []
    arr.extend([1, 2])
    return arr

def insert():
    arr = []
    arr.insert(0, 1)
    arr.insert(1, 2)
    arr.insert(-1, 3)
    arr.insert(len(arr), 4)
    return arr

def index():
    arr = [1, 2, 3, 4, 5]
    return arr.index(4)

def pop():
    arr = [1, 2, 3, 4, 5]
    deleted_items = [arr.pop(), arr.pop(0), arr.pop(1), arr.pop(-1)]
    return deleted_items

def clear():
    arr = [1, 2, 3, 4, 5]
    arr.clear()
    return arr

def count():
    arr = [1, 2, 2]
    res = [arr.count(0), arr.count(1), arr.count(2)]
    return res

def remove():
    arr = [1, 2, 3, 4, 5, 1]
    arr.remove(1)
    arr.remove(4)
    return arr
    
def test_array_methods():
    check_func(append)
    check_func(extend)
    check_func(insert)
    check_func(index)
    check_func(pop)
    check_func(clear)
    check_func(count)
    check_func(remove)
