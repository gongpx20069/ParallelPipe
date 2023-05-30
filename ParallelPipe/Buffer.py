from multiprocessing import Lock, Condition, Queue
import multiprocessing
import threading
from collections import deque
import time

class Buffer(object):
    def __init__(self, size:int, multiprocess:bool=True) -> None:
        self.size       = size
        self.multiprocess = multiprocess
        # self.manager    = Manager()
        # self.buffer     = self.manager.list()
        # self.buffer     = list()
        if multiprocess:
            self.buffer = Queue()
            self.lock = Lock()
            self.is_full = Condition(self.lock)
        else:
            self.buffer = deque(maxlen=self.size)
            # self.lock = threading.Lock()
            self.is_empty = threading.Condition()
            # self.is_full = threading.Condition()
            self.currtime = 0
        # self.has_pos    = Condition(self.lock)

    def __len__(self) -> int:
        return len(self.buffer)

    def get(self) -> any:
        if self.multiprocess:
            result = self.buffer.get()
        else:
            with self.is_empty:
                self.is_empty.wait_for((lambda:((len(self.buffer)>0) and (self.buffer[-1]['time']>self.currtime))))
                result = self.buffer[-1]
                self.currtime=result['time']
                result = result['data']
        return result

    def get_all(self) -> list:
        if self.multiprocess:
            datas = []
            with self.is_full:
                self.is_full.wait_for(lambda:self.buffer.qsize() >= self.size)
                for _ in range(self.size):
                    result = self.buffer.get()
                    datas.append(result)
        else:
            with self.is_empty:
                self.is_empty.wait_for((lambda:((len(self.buffer)==self.size) and (self.buffer[-1]['time']>self.currtime))))
                listbuffer = list(self.buffer)
                self.currtime = listbuffer[-1]['time']
                datas = list(map(lambda x:x['data'], listbuffer))
        return datas

    def put(self, data:any):
        if self.multiprocess:
            with self.is_full:
                self.buffer.put(data)
                self.is_full.notify()

            while self.buffer.qsize() > self.size:
                self.buffer.get()
        else:
            with self.is_empty:
                data={
                    "data":data,
                    "time":time.time(),
                }
                self.buffer.append(data)
                self.is_empty.notify()

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