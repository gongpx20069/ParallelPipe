from __future__ import annotations
from multiprocessing import Process, Queue, Lock
from .Buffer import Buffer
from .Stage import Stage
import threading
import time

class Pipeline(object):
    def __init__(self, stages:list[Stage], end_stage:Stage=None, buffer_size:int=1, multiprocess:int=False) -> bool:
        self.stages     = stages
        self.end_stage = end_stage
        self.stage_num  = len(stages)
        self.multiprocess = multiprocess

        if type(buffer_size) == int:
            self.buffers = [Buffer(size=buffer_size, multiprocess=multiprocess) for _ in range(self.stage_num + 1)]
        elif type(buffer_size) == list:
            try:
                self.buffers = [Buffer(size=buffer_size[i], multiprocess=multiprocess) for i in range(self.stage_num + 1)]
            except:
                raise Exception("length of buffer_size (list) should be equal to length of stages (list)")
        else:
            raise Exception("type of buffer_size should be (int) or (list)")

        if multiprocess:
            self.stage_process = [Process(target=stages[i] , args=(self.buffers[i], self.buffers[i+1])) for i in range(self.stage_num)]
        
            try:
                self.end_process = Process(target=end_stage , args=(self.buffers[-1], None))
            except:
                raise Exception("the end of the pipeline should be a class (class <Stage>)")
        else:
            self.stage_process = [threading.Thread(target=stages[i] , args=(self.buffers[i], self.buffers[i+1])) for i in range(self.stage_num)]
            try:
                self.end_process = threading.Thread(target=end_stage , args=(self.buffers[-1], None))
            except:
                raise Exception("the end of the pipeline should be a class (class <Stage>)")

    def setstop(self):
        if self.multiprocess:
            for stage in self.stage_process:
                stage.terminate()
                stage.join()
            self.end_process.terminate()
            self.end_process.join()
        else:
            for stage in self.stages:
                stage.setstop()
            self.end_stage.setstop()

    def put(self, x:any):
        self.buffers[0].put(x)

    def get(self):
        return self.buffers[-1].get()

    def start(self):
        if self.multiprocess:
            for i in range(self.stage_num):
                self.stage_process[i].start()
            self.end_process.start()

        else:
            for i in range(self.stage_num):
                self.stage_process[i].setDaemon(True)
                self.stage_process[i].start()
            self.end_process.setDaemon(True)
            self.end_process.start()
            
    def __len__(self):
        return self.stage_num


if __name__ == '__main__':
    # queuetest()
    pass