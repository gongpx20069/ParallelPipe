from multiprocessing import Lock, Condition, Queue
import time

class Buffer(object):
    def __init__(self, size):
        self.size       = size
        # self.manager    = Manager()
        # self.buffer     = self.manager.list()
        # self.buffer     = list()
        self.buffer     = Queue()
        self.lock       = Lock()
        self.is_full   = Condition(self.lock)
        # self.has_pos    = Condition(self.lock)

    def __len__(self):
        return len(self.buffer)

    def get(self):
        result = self.buffer.get()
        return result

    def get_all(self):
        datas = []
        with self.is_full:
            self.is_full.wait_for(lambda:self.buffer.qsize() >= self.size)
            result = list(self.buffer)    
        return datas[0:self.size]

    def put(self, data):
        with self.is_full:
            self.buffer.put(data)
            self.is_full.notify()

        while self.buffer.qsize() > self.size:
            self.buffer.get()


# def get1(buffer):
#     print('rev',buffer.get())
         
# def put1(buffer):
#     a = time.time()
#     print('put', a)
#     for _ in range(10):
#         buffer.put(a)

# if __name__ == "__main__":
#     buffer = Buffer(3)
#     th1 = Process(target=put1, args=(buffer,))
#     th2 = Process(target=get1, args=(buffer,))
#     th1.start()
#     th2.start()