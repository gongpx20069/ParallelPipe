from multiprocessing import Process, Queue, Lock
from DeepPipeline.Buffer import Buffer
import time

class Pipeline(object):
    def __init__(self, stages, end_stage = None, buffer_size=1):
        self.stages     = stages
        self.stage_num  = len(stages)

        if type(buffer_size) == type(0):
            self.buffers    = [Buffer(size = buffer_size) for _ in range(self.stage_num + 1)]
        elif type(buffer_size) == list:
            try:
                self.buffers    = [Buffer(size = buffer_size[i]) for i in range(self.stage_num + 1)]
            except:
                raise Exception("length of buffer_size (list) should be equal to length of stages (list)")
        else:
            raise Exception("type of buffer_size should be (int) or (list)")
        self.stage_process = [Process(target = stages[i] , args = (self.buffers[i], self.buffers[i+1])) for i in range(self.stage_num)]
        
        try:
            self.end_stage = Process(target = end_stage , args = (self.buffers[-1], None, True))
        except:
            raise Exception("the end of the pipeline should be a class (class <Stage>)")

    def put(self, x):
        self.buffers[0].put(x)

    def get(self):
        return self.buffers[-1].get()

    def start(self):
        for i in range(self.stage_num):
            self.stage_process[i].start()
        self.end_stage.start()
            
    def __len__(self):
        return self.stage_num


if __name__ == '__main__':
    # queuetest()
    pass