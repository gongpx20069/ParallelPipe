from __future__ import annotations
from multiprocessing import Process, Manager
from .Buffer import Buffer
from .Stage import Stage
import threading

class Pipeline(object):
    def __init__(self, stages:list[Stage], end_stage:Stage=None, buffer_size:int=1, multiprocess:int=False) -> bool:
        self.stages = stages
        if end_stage is not None:
            self.stages.append(end_stage)

        self.stages[-1].set_end_stage()
        self.stage_num = len(self.stages)
        self.multiprocess = multiprocess

        self.manager = Manager() if self.multiprocess else None

        if type(buffer_size) == int:
            self.buffers = [Buffer(size=buffer_size, multiprocess=multiprocess, manager=self.manager) for _ in range(self.stage_num)]
        elif type(buffer_size) == list:
            try:
                self.buffers = [Buffer(size=buffer_size[i], multiprocess=multiprocess) for i in range(self.stage_num)]
            except:
                raise Exception("length of buffer_size (list) should be equal to length of stages (list).")
        else:
            raise Exception("type of buffer_size should be (int) or (list)")

        if self.multiprocess:
            try:
                self.stage_process = [Process(target=self.stages[i], args=(self.buffers[i], self.buffers[i+1])) for i in range(self.stage_num - 1)]
                self.stage_process.append(Process(target=self.stages[-1], args=(self.buffers[-1], None)))
            except:
                raise Exception("the end of the pipeline should be a class (class <Stage>)")
        else:
            try:
                self.stage_process = [threading.Thread(target=self.stages[i], args=(self.buffers[i], self.buffers[i+1])) for i in range(self.stage_num - 1)]
                self.stage_process.append(threading.Thread(target=self.stages[-1], args=(self.buffers[-1], None)))
            except:
                raise Exception("the end of the pipeline should be a class (class <Stage>)")

    def setstop(self):
        for stage in self.stages:
            stage.setstop()
        if self.multiprocess: self.manager.shutdown()

    def put(self, x:any):
        self.buffers[0].put(x)

    def get(self):
        return self.buffers[-1].get()

    def start(self):
        if self.multiprocess:
            for i in range(self.stage_num):
                self.stage_process[i].daemon = True
                self.stage_process[i].start()
        else:
            for i in range(self.stage_num):
                self.stage_process[i].setDaemon(True)
                self.stage_process[i].start()

    def __len__(self):
        return self.stage_num


if __name__ == '__main__':
    # queuetest()
    pass