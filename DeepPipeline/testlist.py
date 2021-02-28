from multiprocessing import Lock, Condition, Process, Manager
import time

def main():
    m = Manager()
    l = m.list()
    l.append(111)
    print(l)

if __name__ == '__main__':
    main()