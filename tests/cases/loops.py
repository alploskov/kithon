def c_for_with_break():
    for i in range(4):
        if i == 2:
            break
        print(i)


def c_for_with_continue():
    for i in range(4):
        if i == 2:
            continue
        print(i)

def c_for_else():
    for i in range(4):
        print(i)
    else:
        print('OK')
    for i in range(4):
        if i == 2:
            break
        print(i)
    else:
        print('NOT OK')

def _foreach():
    for l in ['a', 'b', 'c']:
        print(l)

def while_with_break():
    i = 0
    while True:
        if i == 2:
            break
        print(i)
        i += 1


def while_with_continue():
    i = 0
    while i < 5:
        i += 1
        if i == 2:
            continue
        print(i)

def while_else():
    while True:
        break
    else:
        print('NOT OK')
    i = 0
    while i < 5:
        i += 1
    else:
        print('OK')

def main():
    c_for_with_break()
    c_for_with_continue()
    c_for_else()
    _foreach()
    while_with_break()
    while_with_continue()
    while_else()
main()
