# from multiprocessing import Process
# import os

# def info(title):
#     print(title)
#     print('module name:', __name__)
#     print('parent process:', os.getppid())
#     print('process id:', os.getpid())
#     print('\n')

# def f(name):
#     info('function f')
#     print('hello', name)

# if __name__ == '__main__':
#     info('main line')
#     p = Process(target=f, args=('bob',))
#     p.start()
#     p.join()


class Person:
    def __init__(self, name):
        self.name = name

    def call(self, count=0):
        if count >= 5:
            print(f'End recursion for {self.name}')
            return
        count+=1
        print(f'Count {count}')
        return self.call(count)


p = Person('Ayomide')
p.call()