class A:
    b = 10
    def __init__(self):
        self.c = 100

    def d(self):
        return 1000

    def e(self):
        return self.b

    def f(self):
        self.b = 20
        self.c = 200

def main():
    a = A()
    print(a.b)
    print(a.c)
    print(a.d())
    print(a.e())
    a.f()
    print(a.b)
    print(a.c)

main()
