import random
import time

start = time.process_time_ns()
x = 0
for i in range(10000000):
    # x = random.choice([1,2])
    # x = random.normalvariate(500, 50)
    x = 0.7 * 50000000
end = time.process_time_ns()

print(str((end - start)/1000000000))