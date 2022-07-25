def main():
    print('yes' if True else 'no')
    print('no' if False else 'yes')
    a = 10
    print('yes' if a == 10 else 'no')
    print('no' if a != 10 else 'yes')
    print('yes' if True else 'no' if True else 'no-no')
    print('no' if False else 'yes' if True else 'no-no')
    print('no' if False else 'no-no' if False else 'yes')

main()
