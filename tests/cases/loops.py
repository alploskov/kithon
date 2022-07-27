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


def c_for_with_else():
    for i in range(4):
        print(i)
    else:
        print("OK")

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

def main():
    c_for_with_break()
    c_for_with_continue()
    _foreach()
    while_with_break()
    while_with_continue()

main()
