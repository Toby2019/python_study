import threading
import queue
import time

'''
实现功能：定义一个FIFO的queue,10个元素，3个线程同时来获取
queue线程安全的队列，因此不需要加
thread_lock.acquire()
thread_lock.release()

'''

# 自定义一个线程类，继承threading.Thread，重写__init__和run方法即可
class MyThread(threading.Thread):
    def __init__(self,threadid,name,q):
        threading.Thread.__init__(self)
        self.threadid = threadid
        self.name = name
        self.q =q
        print("%s : Init %s success."%(time.ctime(),self.name))

    def run(self):
        is_empty = False
        while not is_empty:
            thread_lock.acquire()
            if not q.empty():
                data  = self.q.get()
                print("Thread %d get:%d"%(self.threadid,data))
                time.sleep(1)
                thread_lock.release()
            else:
                is_empty = True
                thread_lock.release()

# 定义一个锁
thread_lock = threading.Lock()
# 定义一个FIFO队列
q = queue.Queue()
# 定义线程列表
thread_name_list = ["Thread-1","Thread-2","Thread-3"]
thread_handler_lists = []

# 初始化队列
thread_lock.acquire()
for i in range(10):
    q.put(i)
thread_lock.release()
print("%s : Init queue,size:%d"%(time.ctime(),q.qsize()))

# 初始化线程
thread_id = 1
for thread_name in thread_name_list:
    thread = MyThread(thread_id,thread_name,q)
    thread.start()
    thread_handler_lists.append(thread)
    thread_id += 1

# 等待线程执行完毕
for thread_handler in thread_handler_lists:
    thread_handler.join()

print("%s : End of progress"%(time.ctime()))







