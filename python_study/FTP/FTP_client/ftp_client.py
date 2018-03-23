import socket
import optparse
import json
import os,sys
import hashlib

STATUS_CODE  = {
    250 : "Invalid cmd format, e.g: {'action':'get','filename':'test.py','size':344}",
    251 : "Invalid cmd ",
    252 : "Invalid auth data",
    253 : "Wrong username or password",
    254 : "Passed authentication",
    255 : "Filename doesn't provided",
    256 : "File doesn't exist on server",
    257 : "ready to send file",
    258 : "md5 verification",
    800 : "the file exist,but not enough ,is continue? ",
    801 : "the file exist !",
    802 : " ready to receive datas",
    900 : "md5 valdate success"
}

sk = socket.socket()
sk.connect(("127.0.0.1",18000))

class ClientHander():
    def __init__(self):

        #初始化变量
        self.op = optparse.OptionParser()
        self.op.add_option("-s","--server",dest="server")
        self.op.add_option("-P", "--port", dest="port")
        self.op.add_option("-u", "--username", dest="username")
        self.op.add_option("-p", "--password", dest="password")
        self.options,self.args = self.op.parse_args()
        #self.verify_args(self.options,self.args)
        self.mainPath = os.path.dirname(os.path.abspath(__file__))
        self.last = 0
        self.is_authenticated = False
        self.is_connected = False
        self.is_needed_md5 = True

        #开始建立连接
        self.make_connection()

    # 验证用户输入信息
    def verify_args(self,options,args):
        server = options.server
        port = options.port
        username = options.username
        password = options.password
        if int(port) > 0 and int(port) < 65535:
            return True
        else:
            exit("the port should been in 0-65535")

    # 连接服务器
    def make_connection(self):
        if not self.is_connected:
            self.sock = socket.socket()
            self.sock.connect(("127.0.0.1", 18000))
            self.is_connected = True
        return

    def interactive(self):

        # 判断是否已经验证过
        if not self.is_authenticated:
            self.make_connection()
            self.authenticate()

        # 开始和服务器进行交互
        cmd_info = input("[%s]"%self.current_dir).strip()
        # 利用反射机制，建立命令与功能对应关系
        cmd_list = cmd_info.split()
        if hasattr(self,cmd_list[0]):
            func = getattr(self,cmd_list[0])
            func(*cmd_list)

    def authenticate(self):
        if not self.is_connected:
            print("没有连接FTP服务器")
            return
        if self.options.username is None or self.options.password is None:
            username = input("username:")
            password = input("password:")
            return self.get_auth_result(username,password)
        return self.get_auth_result(self.options.username,self.options.password)

    def response(self):
        data = self.sock.recv(1024).decode("utf-8")
        data = json.loads(data)
        return data

    def get_auth_result(self,username,password):
        data = {
            "action":"auth",
            "username":username,
            "password":password
        }
        self.sock.send(json.dumps(data).encode("utf-8"))
        res = self.response()
        print("res",res["status_code"])
        if res["status_code"] ==  254:
            self.username = username
            self.current_dir = username
            self.is_authenticated = True
            print(STATUS_CODE[254])
            return True
        else:
            print(STATUS_CODE[res["status_code"]])

    def put(self,*cmd_list):

        # 1 发送上传命令
        action,local_path,target_path = cmd_list
        local_path = os.path.join(self.mainPath,local_path)
        file_name = os.path.basename(local_path)
        file_size = os.stat(local_path).st_size
        data = {
            "action":"put",
            "file_name": file_name,
            "file_size": file_size,
            "target_path": target_path
        }
        self.sock.sendall(json.dumps(data).encode("utf-8"))

        # 2 接收服务器检查结果
        has_sent = 0
        is_exsit = self.sock.recv(1024).decode("utf-8")

        # 3 根据服务器检查结果，执行相应命令
        # 文件存在但不完整
        if is_exsit == "800":
            print("服务器文件已经存在，且不完整")
            # 和服务器确认是否继续上传
            choice = input("The file exist but not enough,is continue?[Y/N]").strip()
            # 继续上传
            if choice.upper() == "Y":
                self.sock.sendall("Y".encode("utf-8"))
                # 等待服务器返回存在文件大小
                continue_position = self.sock.recv(1024).decode("utf-8")
                has_sent += int(continue_position)
            # 不继续上传
            else:
                self.sock.sendall("N".encode("utf-8"))
        # 文件存在且完整
        elif is_exsit == "801":
            print("服务器文件已经存在，且完整")
            return
        f = open(local_path,"rb")
        f.seek(has_sent)

        md5_obj = None
        if self.is_needed_md5:
            md5_obj = hashlib.md5()

        while has_sent < file_size:
            data = f.read(1024)
            self.sock.sendall(data)
            if md5_obj:
                md5_obj.update(data)
            has_sent += len(data)

        mdt_val_server = self.sock.recv(1024).decode("utf-8")
        mdt_val_client = md5_obj.hexdigest()
        self.show_progress(has_sent,file_size)
        print("client's md5 is %s"%mdt_val_client)
        print("server's md5 is %s" %mdt_val_server)
        f.close()

        if mdt_val_client == mdt_val_server:
            print("put success")
        else:
            print("Athenticate MD5 failed.")

    def show_progress(self,has,total):
        rate = float(has) / float(total)
        rate_num = int(rate*100)
        print("%s%% %s\r"%(rate_num,"#"*rate_num))

    def ls(self,*cmd_list):
        data = {
            "action":"ls"
        }
        self.sock.sendall(json.dumps(data).encode("utf-8"))
        data = self.sock.recv(1024).decode("utf-8")
        print(data)

    def cd(self,*cmd_list):
        # cd images
        data = {
            "action":"cd",
            "dirname":cmd_list[1]
        }
        self.sock.sendall(json.dumps(data).encode("utf-8"))
        data = self.sock.recv(1024).decode("utf-8")
        self.current_dir = os.path.basename(data)
        print(os.path.basename(data))

    def mkdir(self,*cmd_list):
        data = {
            "action":"mkdir",
            "dirname":cmd_list[1]
        }

        self.sock.sendall(json.dumps(data).encode("utf-8"))
        data = self.sock.recv(1024).decode("utf-8")
        print(data)

ch = ClientHander()
while 1:
    ch.interactive()
