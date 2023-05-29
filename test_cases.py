from DeepPipeline import Pipeline, Stage
import time

class stage_one(Stage):        
    def stage_run(self, x):
        time.sleep(0.5)
        x.append("stage one")
        return x

class stage_two(Stage):
    def stage_run(self, x):
        time.sleep(0.5)
        x.append("stage two")
        return x

class stage_three(Stage):
    def stage_run(self, x):
        time.sleep(0.5)
        x.append("stage three")
        return x

class stage_end(Stage):
    def stage_run(self, x):
        print(x)


if __name__ == '__main__':
    one = stage_one()
    two = stage_two()
    three = stage_three()
    end = stage_end()

    P = Pipeline(stages = [one, two, three], end_stage = end, buffer_size = 2, multiprocess=True)
    P.start()
    
    for i in range(1, 11):
        try:
            P.put(["Pipeline: {}".format(i)])
            time.sleep(0.3)
        except (Exception,KeyboardInterrupt) as ep:
                raise ep
    P.setstop()