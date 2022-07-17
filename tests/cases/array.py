def main():
    arr1 = [1,2,3,4,5,6,7,8,9,0]
    
    _index = 5
    print(arr1[_index] == 6)
    
    _index = -2
    print(arr1[_index] == 9)
    
    print(arr1[0] == 1)
    print(arr1[-1] == 0)
    print(arr1[1:-1] == [2,3,4,5,6,7,8,9])
    print(arr1[1:-1:2] == [2,4,6,8])
    print(arr1[1:] == [2,3,4,5,6,7,8,9,0])
    print(len(arr1) == 10)


    arr2 = []
    for i in range(10):
        arr2.append(i)

    _index = 5
    print(arr2[_index] == 5)

    _index = -2
    print(arr2[_index] == 8)
    
    print(arr2[0] == 0)
    print(arr2[-1] == 9)
    print(arr2[1:-1] == [1,2,3,4,5,6,7,8])
    print(arr2[1:] == [1,2,3,4,5,6,7,8,9])
    print(len(arr2) == 10)

    arr3 = [1]*10
    print(arr3 == [1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    print(len(arr3) == 10)

    arr4 = [1,2]*10
    print(arr4 == [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2])
    print(len(arr4) == 20)
    arr5 = [[1,2,3,4,5],
            [1,2,3,4,5],
            [1,2,3,4,5],
            [1,2,3,4,5],
            [1,2,3,4,5]]
    for i in arr5:
        print(i == [1,2,3,4,5])
main()
