from abc import ABCMeta, abstractmethod


class Stage(metaclass = ABCMeta):
    '''
    stage_run: base class for the multi-stage pipline. 
    '''
    def __init__(self):
        self.is_get_all = False

    def set_get_all(self):
        self.is_get_all = True

    @abstractmethod
    def stage_run(self, x):
        pass

    def read_x_from_buffer(self, buffer):
        if self.is_get_all:
            return buffer.get_all()
        else:
            return buffer.get()

    def write_y_to_buffer(self, y, buffer):
        buffer.put(y)

    def __stage(self, per_buffer, next_buffer):
        x = self.read_x_from_buffer(buffer = per_buffer)
        y = self.stage_run(x)
        self.write_y_to_buffer(y = y, buffer = next_buffer)

    def __end_stage(self, per_buffer):
        x = self.read_x_from_buffer(buffer = per_buffer)
        y = self.stage_run(x)
        # self.write_y_to_buffer(y = y, buffer = next_buffer)

    def __call__(self, per_buffer, next_buffer = None, is_end = False):
        while True:
            try:
                if not is_end:
                    self.__stage(per_buffer, next_buffer)
                else:
                    self.__end_stage(per_buffer)
            except Exception as ep:
                raise ep