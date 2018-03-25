import threading
import queue
import time

'''
实现功能：定义一个FIFO的queue,10个元素，3个线程同时来获取
'''

# 初始化FIFO队列
q = queue.Queue()
for i in range(10):
    q.put(i)
print("%s : Init queue,size:%d"%(time.ctime(),q.qsize()))

# 线程功能函数，获取队列数据
def run(q,threadid):
    is_empty = False
    while not is_empty:
        if not q.empty():
            data  = q.get()
            print("Thread %d get:%d"%(threadid,data))
            time.sleep(1)
        else:
            is_empty = True

# 定义线程列表
thread_handler_lists = []
# 初始化线程
for i in range(3):
    thread = threading.Thread(target=run,args = (q,i))
    thread.start()
    thread_handler_lists.append(thread)
# 等待线程执行完毕
for thread_handler in thread_handler_lists:
    thread_handler.join()

print("%s : End of progress"%(time.ctime()))

