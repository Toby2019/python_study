'''
程序欲实现功能：定义两个CPU占用高函数，测试Python多进程执行效率
'''

import multiprocessing
import time

def sum():
    sum = 0
    for i in range(100000000):
        sum += i

def mul():
    sum = 0
    for i in range(1000000000):
        sum *= i

if __name__ == "__main__":
    start_time = time.time()
    # 执行两个函数
    mul()
    mul()
    end_time = time.time()
    print("single proccess cost : %d" % (end_time - start_time))

    start_time = time.time()
    #定义两个进程
    l = []
    p1 = multiprocessing.Process(target = mul)
    p1.start()
    l.append(p1)

    p2 = multiprocessing.Process(target = mul)
    p2.start()
    l.append(p2)

    for p_list in l:
        p_list.join()

    end_time = time.time()
    print("Mutiple proccess cost : %d"%(end_time - start_time))


