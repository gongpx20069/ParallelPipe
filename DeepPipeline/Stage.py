from abc import ABCMeta, abstractmethod
from .Buffer import Buffer

class Stage(metaclass = ABCMeta):
    '''
    stage_run: base class for the multi-stage pipline. 
    '''
    def __init__(self):
        self.is_get_all = False
        self.__stop = False

    def setstop(self):
        self.__stop = True

    def set_get_all(self):
        self.is_get_all = True

    def set_get_single(self):
        self.is_get_all = False

    @abstractmethod
    def stage_run(self, x:any):
        pass

    def read_x_from_buffer(self, buffer:Buffer):
        if self.is_get_all:
            return buffer.get_all()
        else:
            return buffer.get()

    def write_y_to_buffer(self, y:any, buffer:Buffer):
        buffer.put(y)

    def __stage(self, per_buffer:Buffer, next_buffer:Buffer):
        x = self.read_x_from_buffer(buffer = per_buffer)
        y = self.stage_run(x)
        self.write_y_to_buffer(y = y, buffer = next_buffer)

    def __end_stage(self, per_buffer:Buffer):
        x = self.read_x_from_buffer(buffer = per_buffer)
        y = self.stage_run(x)
        # self.write_y_to_buffer(y = y, buffer = next_buffer)

    def __call__(self, per_buffer:Buffer, next_buffer:Buffer=None):
        while not self.__stop:
            if next_buffer is not None:
                self.__stage(per_buffer, next_buffer)
            else:
                self.__end_stage(per_buffer)