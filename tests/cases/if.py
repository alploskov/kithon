def if_():
    if True:
        print('ok')

def if_else():
    if True:
        print('ok')
    else:
        print('error')

    if False:
        print('error')
    else:
        print('ok')

def if_elif():
    if True:
        print('ok')
    elif True:
        print('error')

    if False:
        print('error')
    elif True:
        print('ok')

def if_elif_else():
    if True:
        print('ok')
    elif True:
        print('error')
    else:
        print('error')

    if False:
        print('error')
    elif True:
        print('ok')
    else:
        print('error')

    if False:
        print('error')
    elif False:
        print('error')
    else:
        print('ok')

def main():
    if_()
    if_else()
    if_elif()
    if_elif_else()

main()
