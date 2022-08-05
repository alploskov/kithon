def _append():
    arr = [1,2,3,4]
    print(arr)
    arr.append(5)
    print(arr)

def _clear():
    arr = [1, 2, 3, 4, 5]
    print(arr)
    arr.clear()
    print(arr)

def _count():
    arr = [1, 1, 2, 3, 4]
    print(arr.count(0))
    print(arr.count(1))
    print(arr.count(2))

def _extend():
    arr = [1]
    print(arr)
    arr.extend([2, 3, 4, 5])
    print(arr)

def _index():
    arr = [1, 2, 3]
    print(arr.index(1))
    print(arr.index(2))
    print(arr.index(3))

def _insert():
    arr = [1, 3, 4]
    print(arr)
    arr.insert(1, 2)
    print(arr)

def _remove():
    arr = [1, 1, 2, 3]
    print(arr)
    arr.remove(1)
    print(arr)

def _reverse():
    arr = [3,2,1]
    print(arr)
    arr.reverse()
    print(arr)

def _sort():
    arr = [1, 3, 2]
    print(arr)
    arr.sort()
    print(arr)

def main():
    _append()
    _clear()
    _count()
    _extend()
    _index()
    _insert()
    _remove()
    _reverse()
    _sort()
main()
