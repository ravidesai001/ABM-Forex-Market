import random
import time

start = time.process_time_ns()
x = []
for i in range(10000000):
    r = random.random()
    x.append(0) if r < 0.5 else x.append(1)
    # r = random.choice([0, 1])
    # x.append(r)
end = time.process_time_ns()
print(sum(x) / float(len(x)))
print(str((end - start)/1000000000))