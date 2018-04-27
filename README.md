# quicksimd

Quicksimd is a simple wrapper to process data multithreaded with low effort.

## Installation

`pip install -e .`

## Usage

The `Simd` class requires a `setup` and a `task` function.
It manages parallelism and provides `get` and `put` function to add/take data to/from its queues.

### Setup

The `setup` function takes an arbitrary global data object that should be available to all threads.
It can process this object and/or generate thread local data that is unique for each thread.
It should return everything that is required inside the thread (global and thread local data together).

### Task

The `task` function implements the functionality that shall be executed on each piece of data.
It gets the data returned from `setup` and one single datum from the queue.
It can return a datum that is put into the output queue.

## Usage Example

This example generates arbitrary checksums on numbers.

```
import quicksimd

data = [1, 2, 3, 4, 5, 6, 7, 8, ...]

def setup(hash):
    return hash

def task(hash, datum):
    return (datum, hash(datum))

simd = quicksimd.Simd(setup, task)

# use 5 threads
simd.run(5)

# fill the queue, processing starts with the first element being put
for x in data:
    simd.put(x)
    # instantly take processed elements from the queue
    print(simd.get())
```

The previous example isn't optimal as it only puts and takes one element a time not really using the threading.
For this case quicksimd supports generators:

```
import quicksimd

# generator that generates increasing numbers
def count():
    x = 0
    while True:
        x += 1
        yield x

def setup(divider)
    return divider

# only return numbers that can be divided by divider
def task(divider, number)
    if number % divider == 0:
        return number

simd = quicksimd.Simd(setup, task)

# use 5 threads, pass 7 as divider to setup
simd.run(5, 7)

# automatically fill the input queue with up to 100 values from the generator (nonblocking, take() would be blocking)
simd.take_background(count(), 100)

# results is a generator that provides the output values, in this case its a generator for numbers divisible by 7
for i in simd.results():
    print(i)
```

## Notes

Currently only threading is supported.
Due to the [GIL](https://en.wikipedia.org/wiki/Global_interpreter_lock) this does not yield more computing power.
Yet it is useful for I/O operations (e.g. networking with multiple connections).

Multiprocessing is planned to be supported in the future.

