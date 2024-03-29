from utils import check_func


def c_for():
    res: list[int] = []
    for i in range(10):
        res.append(i)
    return res

def c_for_countdown():
    res = []
    for i in range(10, 0, -1):
        res.append(i)
    return res

def c_for_with_break():
    res = []
    for i in range(4):
        if i == 2:
            break
        res.append(i)
    return res

def c_for_with_continue():
    res = []
    for i in range(4):
        if i == 2:
            continue
        res.append(i)
    return res

def c_for_else():
    res = []
    for i in range(4):
        res.append(i)
    else:
        res.append(100)
    for i in range(4):
        if i == 2:
            break
        res.append(i)
    else:
        res.append(-100)
    return res

def test_c_for():
    check_func(c_for)
    check_func(c_for_countdown)
    check_func(c_for_with_break)
    check_func(c_for_with_continue)
    check_func(c_for_else)


def foreach():
    res = []
    for l in ['a', 'b', 'c']:
        res.append(l)
    return res

def test_foreach():
    check_func(foreach)


def while_with_break():
    res = []
    i = 0
    while True:
        if i == 2:
            break
        res.append(i)
        i += 1
    return res

def test_while():
    check_func(while_with_break)
