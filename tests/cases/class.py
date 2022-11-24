class A:
    b = 10
    def __init__(self):
        self.c = 100

    def d(self):
        return 1000

    def e(self):
        return self.b

def main():
    a = A()
    print(a.b)
    print(a.c)
    print(a.d())
    print(a.e())

main()
