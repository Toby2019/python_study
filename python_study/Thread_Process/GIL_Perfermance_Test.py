import threading
import time

# 定义两个计算量大的函数
def sum():
    sum = 0
    for i in range(100000000):
        sum += i

def mul():
    sum = 0
    for i in range(10000000):
        sum *= i

# 单线程时间测试
starttime = time.time()
sum()
mul()
endtime = time.time()
period = endtime - starttime
print("The single thread cost:%d"%(period))

# 多线程时间测试
starttime = time.time()
l = []
t1 = threading.Thread(target = sum)
t2 = threading.Thread(target = sum)
l.append(t1)
l.append(t2)
for i in l:
    i.start()
for i in l:
    i.join()
endtime = time.time()
period = endtime - starttime
print("The mutiple thread cost:%d"%(period))


print("End of program.")

