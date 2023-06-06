from multiprocessing import Condition
import multiprocessing
import threading
from collections import deque
import time

class Buffer(object):
    def __init__(self, size:int, multiprocess:bool=True, manager:multiprocessing.Manager=None) -> None:
        self.size = size
        self.multiprocess = multiprocess
        self.currtime = 0
        if multiprocess:
            self.buffer = manager.list()
            self.is_empty = Condition()
        else:
            self.buffer = deque(maxlen=self.size)
            self.is_empty = threading.Condition()

    def __len__(self) -> int:
        return len(self.buffer)

    def get(self) -> any:
        if self.multiprocess:
            with self.is_empty:
                self.is_empty.wait_for((lambda:((len(self.buffer)>0) and (self.buffer[-1]['time']>self.currtime))))
                result = self.buffer.pop()
                self.currtime = result['time']
                result = result['data']
        else:
            with self.is_empty:
                self.is_empty.wait_for((lambda:((len(self.buffer)>0) and (self.buffer[-1]['time']>self.currtime))))
                result = self.buffer[-1]
                self.currtime = result['time']
                result = result['data']
        return result

    def get_all(self) -> list:
        if self.multiprocess:
            with self.is_empty:
                self.is_empty.wait_for((lambda:((len(self.buffer)==self.size) and (self.buffer[-1]['time']>self.currtime))))
                self.currtime = self.buffer[-1]['time']
                datas = list(map(lambda x:x['data'], self.buffer))
        else:
            with self.is_empty:
                self.is_empty.wait_for((lambda:((len(self.buffer)==self.size) and (self.buffer[-1]['time']>self.currtime))))
                listbuffer = list(self.buffer)
                self.currtime = listbuffer[-1]['time']
                datas = list(map(lambda x:x['data'], listbuffer))
        return datas

    def put(self, data:any):
        with self.is_empty:
            data={
                "data":data,
                "time":time.time(),
            }
            self.buffer.append(data)
            self.is_empty.notify()

            if self.multiprocess:
                while len(self.buffer) > self.size:
                    self.buffer.pop(0)