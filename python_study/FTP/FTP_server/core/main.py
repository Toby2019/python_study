import optparse
import socketserver
from conf import settings
from core import server

class ArgvHandler():

    def __init__(self):
        self.op = optparse.OptionParser()
        #self.op.add_option("-s","--server",dest = "server")
        #self.op.addd_option("-P", "--port", dest="port")

        options,args = self.op.parse_args()
        self.verify_args(options,args)


    def verify_args(self,options,args):
        #首先判断参数的长度
        if len(args) < 1:
            print("参数个数太少，请重新输入.")
        else:
            cmd = args[0]
            if hasattr(self,cmd):
                func = getattr(self,cmd)
                func()
        self.start()

    def start(self):
        s = socketserver.ThreadingTCPServer((settings.IP,settings.PORT),server.ServerHandler)
        print("服务器已经启动")
        s.serve_forever()

    def help(self):
        pass
