from utils import check_func


def if_():
    if True:
        return True

def if_else():
    if True:
        return True
    else:
        return False

    if False:
        return False
    else:
        return True

def if_elif():
    if True:
        return True
    elif True:
        return False

    if False:
        return False
    elif True:
        return True

def if_elif_else():
    if True:
        return True
    elif True:
        return False
    else:
        return False

    if False:
        return False
    elif True:
        return True
    else:
        return False

    if False:
        return False
    elif False:
        return False
    else:
        return True

def test_if():
    check_func(if_)
    check_func(if_else)
    check_func(if_elif)
    check_func(if_elif_else)
