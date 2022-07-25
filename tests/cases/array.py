def get_by_index():
    arr = [1,2,3,4]
    print(arr[0])
    print(arr[1])
    print(arr[-1])
    print(arr[-2])

def lens():
    print(len([]))
    print(len([1]))
    print(len([1, 2, 3]))

def slices():
    arr = [1, 2, 3, 4, 5, 6]
    print(arr[:])
    print(arr[0:])
    print(arr[1:])

    print(arr[:-1])
    print(arr[0:-1])
    print(arr[1:-1])
    print(arr[-1:1])
    
    print(arr[::1])
    print(arr[::-1])
    print(arr[1:-1:2])
#    print(arr[-1:1:-1])
#    print(arr[-1:1:-2])

def main():
    print([])
    print([1])
    print([1,2,3,4])
    get_by_index()
    slices()

main()
