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

def test_bit_ops():
    nums = [-10, -2, -1, 0, 1, 2, 10]
    exprs = []
    for n1 in nums:
        for n2 in nums:
            exprs.append(f'{n1} & {n2}')
            exprs.append(f'{n2} & {n1}')
            exprs.append(f'{n1} | {n2}')
            exprs.append(f'{n2} | {n1}')
            exprs.append(f'{n1} ^ {n2}')
            exprs.append(f'{n2} ^ {n1}')
            if n2 > 0:
                exprs.append(f'{n1} << {n2}')
                exprs.append(f'{n1} >> {n2}')
            if n1 > 0:
                exprs.append(f'{n2} << {n1}')
                exprs.append(f'{n2} >> {n1}')
        exprs.append(f'~{n1}')
    check_exprs(exprs)
