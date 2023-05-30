<h2 align="center">Python Parallel Pipeline Architecture (ParallelPipe)</h2>
<p align="center">
Language: <a href="https://github.com/gongpx20069/ParallelPipe#readme" target="_blank" rel="noopener noreferrer">English</a>
  | <a href="https://github.com/gongpx20069/ParallelPipe#readme" target="_blank" rel="noopener noreferrer">中文</a>
</p>

-------------------------

## Write in advance

You can install this package using the following command:

```pip install PyParallelPipe```

### 1. Overview
In deep learning, many tasks in practical business scenarios are multi-stage and decomposable. Taking behavior recognition as an example, when performing behavior recognition using RGB video streams, we can divide the overall workflow into four steps: data collection, object recognition, object tracking, and behavior classification, as shown in Figure 1. If these four steps are executed sequentially, it would consume a significant amount of time. However, if these four steps can run simultaneously, it often enables real-time processing in practical applications, overcoming the time-consuming nature of sequential execution.

The design principles of the framework are: **decoupling, reusability, readability, and high performance**.

[![pipeline_zh](docs/pipeline_zh.png)](https://github.com/gongpx20069/ParallelPipe/blob/main/docs/pipeline_zh.png)

#### 1.1 Environment Requirements
This framework can run in a Python 3.5+ environment without requiring any additional Python dependencies.

#### 1.2 Python Dependencies
To avoid the Global Interpreter Lock (GIL) in Python for multithreading, we plan to use the following built-in Python libraries:

multiprocessing: Ensures parallel utilization of multiple CPU cores (you can choose the multiprocessing model).

Time&Queue: Uses timestamps to ensure information exchange between queues as buffers and multithreading locks to ensure data consistency in read and write operations.

### 2. How to Use
#### 2.1 Quick Start
1. First, we need to define processing tasks for different stages. For example:
```python
   class stage_one(Stage):
       def stage_run(self, x):
           time.sleep(0.5)
           x.append("stage one")
           return x
   ```
In this example, each individual stage task must inherit the Stage class from the ParallelPipe package and implement the stage_run(x) method. The input x of stage_run(x) is the output from the previous stage, and the return value y is the processing result of the current stage.

2. In addition to regular individual stage processing tasks, we also need to define the final output task of the pipeline (e.g., video display, data storage). In this case, we still need to inherit the Stage class from ParallelPipe, but no return value is required. Here's an example:
```python
   class stage_end(Stage):
    def stage_run(self, x):
        print(x)
   ```

3. After defining all the individual stage tasks, we need to instantiate the `Pipeline` class from the `ParallelPipe` package and specify the final output stage. Here is an example program:
```python
P = Pipeline(stages=[one, two, three], end_stage=end, buffer_size=2, multiprocess=False)
```
In the above code, `one`, `two`, `three`, and `end` are instances of classes that inherit from the `Stage` class and implement the `stage_run` function. The `buffer_size` parameter determines the buffer size between different stages for information exchange during adjacent stages.

In this example, the `multiprocess` parameter is set to `False`, which means the pipeline will use multithreading instead of multiprocessing. If you set it to `True`, the pipeline will utilize multiple processes instead.

4. Run the entire workflow:
   ```python
   P.start()
   ```
   Once the framework is started, you can use the `put` function of the `Pipeline` class to add inputs to the framework:
   ```
   P.put("Something Stage one can process.")
   ```
5. After completing all the work, you can call the `setstop` function of the `Pipeline` class to guide the termination of all subprograms:
   ```
   P.setstop()
   ```

The overall test code mentioned above is as follows:

```python
from ParallelPipe import Pipeline, Stage
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

    P = Pipeline(stages = [one, two, three, end], buffer_size = 2, multiprocess=True)
    P.start()
    
    for i in range(1, 11):
        try:
            P.put(["Pipeline: {}".format(i)])
            time.sleep(0.3)
        except (Exception,KeyboardInterrupt) as ep:
                raise ep
    P.setstop()
```

output:

```python
['Pipeline: 1', 'stage one', 'stage two', 'stage three']
['Pipeline: 2', 'stage one', 'stage two', 'stage three']
['Pipeline: 3', 'stage one', 'stage two', 'stage three']
['Pipeline: 5', 'stage one', 'stage two', 'stage three']
['Pipeline: 7', 'stage one', 'stage two', 'stage three']
['Pipeline: 8', 'stage one', 'stage two', 'stage three']
['Pipeline: 9', 'stage one', 'stage two', 'stage three']
['Pipeline: 10', 'stage one', 'stage two', 'stage three']
```

#### 2.2 `Stage` Class

The `Stage` class is provided by the ParallelPipe package, and each individual stage task must inherit this class and implement the `stage_run(x)` method. In the equation `y = stage_run(x)`, `x` represents the output from the previous stage, and `y` represents the processing result of the current stage.

For example, consider the following code:

```python
class stage_one(Stage):
    def stage_run(self, x):
        time.sleep(0.5)
        x.append("stage one")
        return x
```

In this code, the `stage_one` class inherits the `Stage` class and implements the `stage_run` method. The input `x` is the output from the previous stage, and the return value `y` is the processing result of the current stage.

If you need multiple sample inputs (i.e., you need all the outputs from the previous stage in the buffer), you can use the `set_get_all()` method on the instantiated class. For example:

```python
one = stage_one()
one.set_get_all()
```

Similarly, you can also specify that the current stage requires single sample input (which is the default behavior). You can achieve this by using the `set_get_single()` method. For example:

```python
one = stage_one()
one.set_get_single()
```

By default, a stage expects to receive a single sample as input. However, if you have a stage that needs to process multiple samples at once, you can call the `set_get_all()` method to receive all samples from the previous stage in the buffer.

#### 2.3 `Pipeline` class

The `Pipeline` class is instantiated with the following optional parameters:

```python
P = Pipeline(stages=[one, two, three, end], buffer_size=2, multiprocess=True)
```

Where:

- `stages`: A list of instantiated subclasses of the `Stage` class representing the multiple stages in the pipeline.

- `buffer_size`: The size of the data exchange buffer between adjacent stages. It can be either a single integer value or a list of integers. If it is a list, it must have the same length as the `stages` list. For example, if there are 4 stages, the `buffer_size` list should have a size of 4.

**[ Regarding `buffer_size`, we prepare a buffer for each stage as input, so the list size is `len(stages)` ]**.

Once all the preparations are complete, you can start the overall workflow by calling:
```python
P.start()
```

After the framework is started, you can use the `put` function of the `Pipeline` class to add inputs to the framework:
```
P.put("Something Stage one can process.")
```

You can add inputs to the pipeline using the `put` function as needed. The pipeline will automatically distribute the inputs to the appropriate stages for processing.

--------------------------------

## 简单安装

你可以使用如下命令安装本Python包：

```pip install PyParallelPipe```

### 1. 概述

在深度学习中，很多实际业务场景中的任务是多阶段的，可拆解的任务。如图1，以行为识别为例，在使用RGB视频流进行行为识别时，我们可以将整体工作流分为四个步骤（数据采集、目标识别、目标追踪、行为分类）。如果四个步骤串行运行，则会占用大量的时间。如果四个步骤可以同时运行，往往可以使串行占用大量时间的方法在实际业务中实时进行。

框架设计宗旨为：**解耦，可复用，易理解，高性能。**

[![pipeline_zh](docs/pipeline_zh.png)](https://github.com/gongpx20069/ParallelPipe/blob/main/docs/pipeline_zh.png)

#### 1.1 使用环境

本框架可以在python3.5+的环境中运行，无需额外的Python依赖包。

#### 1.2 Python依赖

为避免Python语言多线程的GIL，我们计划使用如下Python自有的库：

- multiprocessing：多进程保证多核CPU并行使用（可以选择多进程模型）；

- Time&Queue：时间戳保证Queue作为Buffer中信息的交换中介；多线程锁保证读写一致性；

### 2. 如何使用

#### 2.1 快速使用

1. 首先我们需要编写不同阶段的处理任务，比如：

   ```python
   class stage_one(Stage):
       def stage_run(self, x):
           time.sleep(0.5)
           x.append("stage one")
           return x
   ```
   其中，每个单阶段任务都必须继承ParallelPipe包中的Stage类，并实现stage_run(x)方法，y = stage_run(x)中输入x是上一阶段的输出，返回值y是本阶段的处理结果。
   
2. 除了正常的单阶段处理任务，我们还需要定义一下流水线最终的输出任务（比如：视频展示、数据保存），这时我们依然需要继承ParallelPipe中的Stage类，不过不需要返回值。以如下程序为例：
   ```python
   class stage_end(Stage):
    def stage_run(self, x):
        print(x)
   ```
   
3. 在定义完成所有的单阶段任务后，我们需要实例化ParallelPipe包中的Pipeline类，并指明最终的输出阶段。以如下程序为例（其中，multiprocess为True时，调用多进程，为False时，调用多线程）：
   ```python
   P = Pipeline(stages = [one, two, three], end_stage = end, buffer_size = 2, multiprocess=False)
   ```
   其中，one, two, three, end为继承了Stage类并实现了stage_run函数的类的实例。buffer_size=2为不同阶段之间的缓冲区大小（进行相邻阶段之间的信息交互）。
   
4. 运行整体工作流：
   ```python
   P.start()
   ```
   在框架启动后，我们可以使用Pipeline类中的put函数来为框架添加输入：
   ```
   P.put("Something Stage one can process.")
   ```
5. 再完成所有的工作后，我们可以调用Pipeline的setstop引导所有子程序结束，：

   ```
   P.setstop()
   ```

   

以上介绍的整体测试代码如下：

```python
from ParallelPipe import Pipeline, Stage
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

    P = Pipeline(stages = [one, two, three, end], buffer_size = 2, multiprocess=True)
    P.start()
    
    for i in range(1, 11):
        try:
            P.put(["Pipeline: {}".format(i)])
            time.sleep(0.3)
        except (Exception,KeyboardInterrupt) as ep:
                raise ep
    P.setstop()
```

最终输出为：

```python
['Pipeline: 1', 'stage one', 'stage two', 'stage three']
['Pipeline: 2', 'stage one', 'stage two', 'stage three']
['Pipeline: 3', 'stage one', 'stage two', 'stage three']
['Pipeline: 5', 'stage one', 'stage two', 'stage three']
['Pipeline: 7', 'stage one', 'stage two', 'stage three']
['Pipeline: 8', 'stage one', 'stage two', 'stage three']
['Pipeline: 9', 'stage one', 'stage two', 'stage three']
['Pipeline: 10', 'stage one', 'stage two', 'stage three']
```
#### 2.2 Stage类
每个单阶段任务都必须继承ParallelPipe包中的Stage类，并实现stage_run(x)方法，y = stage_run(x)中输入x是上一阶段的输出，返回值y是本阶段的处理结果。
   ```python
class stage_one(Stage):
    def stage_run(self, x):
        time.sleep(0.5)
        x.append("stage one")
        return x
   ```

对于`y = stage_run(x)`函数，x一般为上一阶段的单个样本输出，y为本阶段数据处理的单个样本输出。当我们需要多个样本输入时（需要上一阶段在缓存区所有的输出时），需要对实例化后的类进行`set_get_all()`，以如下程序为例：

```python
one = stage_one()
one.set_get_all()
```

同理，我们也可以指定当前阶段需要单个样本输入（默认为单个样本输入）：
```python
one = stage_one()
one.set_get_single()
```

#### 2.3 Pipeline类

Pipeline类有如下可选参数进行实例初始化：

```python
P = Pipeline(stages = [one, two, three, end], buffer_size = 2, multiprocess=True)
```

其中：

- stages: list[Stage]，多阶段类（Stage）子类的实例化的列表；

- buffer_size: list or int，相邻阶段的数据交换缓冲区大小，如果是list类型，必须和stage的长度一致，比如：当存在4个单阶段任务时，buffer_size的列表大小为4。

  【对于buffer_size，我们为每个阶段都准备了一个buffer作为输入，因此共有len(stages)的列表大小。】

在一切准备完成后，我们只需要运行整体工作流：
   ```python
   P.start()
   ```
在框架启动后，我们可以使用Pipeline类中的put函数来为框架添加输入：
   ```
   P.put("Something Stage one can process.")
   ```
