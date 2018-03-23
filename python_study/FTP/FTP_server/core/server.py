
import socketserver
import json
import configparser
from conf import settings
import os
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


class ServerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        while 1:
            data = self.request.recv(1024).strip()
            if not data:continue
            data = json.loads(data.decode("utf-8"))

            if data.get("action"):
                if hasattr(self,data.get("action")):
                    func = getattr(self,data.get("action"))
                    func(**data)
                else:
                    print("Invalid cmd")
            else:
                print("Invalid cmd")

    def send_response(self,status_code):
        response = {"status_code":status_code}
        self.request.sendall(json.dumps(response).encode("utf8"))

    def auth(self,**data):
        username = data["username"]
        password = data["password"]
        print("收到客户端验证请求，用户名：",username,"密码：",password)
        user = self.authenticate(username,password)
        if user:
            self.send_response(254)
        else:
            self.send_response(253)

    def authenticate(self,username,password):
        cfg = configparser.ConfigParser()
        cfg.read(settings.ACCOUNT_PATH)
        print("正在读取配置用户配置信息：",settings.ACCOUNT_PATH)

        if username in cfg.sections():
            if cfg[username]["Password"] == password:
                self.useranme = username
                self.mainPath = os.path.join(settings.BASE_DIR,"home",self.useranme)
                print("成功匹配上用户信息,用户密码:", cfg[username]["Password"])
                print("用户根目录为:",self.mainPath)
                return username

    def put(self,**data):
        print("data",data)
        file_name = data.get("file_name")
        file_size = data.get("file_size")
        target_path = data.get("target_path")

        abs_path = os.path.join(self.mainPath,target_path,file_name)

        has_received = 0

        if os.path.exists(abs_path):
            file_has_size = os.stat(abs_path).st_size
            if file_has_size < file_size:
                #断点续传
                self.request.sendall("800".encode("utf-8"))
                choice = self.request.recv(1024).decode("utf-8")
                if choice.upper() == "Y":
                    self.request.sendall(str(file_has_size).encode("utf-8"))
                    f = open(abs_path,"ab")
                    has_received += file_has_size
                else:
                    f = open(abs_path,"wb")
            else:
                #文件完全存在
                self.request.sendall("801".encode("utf-8"))
                return
        else:
            self.request.sendall("802".encode("utf-8"))
            f = open(abs_path, "wb")

        md5_obj = hashlib.md5()

        while has_received < file_size:
            try:
                data = self.request.recv(1024)
                f.write(data)
                md5_obj.update(data)
                has_received += len(data)
            except Exception as e:
                print("传输文件发生异常：",str(e))
                break

        # 给客户端发送MD5
        md5_val = md5_obj.hexdigest()
        self.request.sendall(md5_val.encode("utf-8"))

        f.close()

    def ls(self,**data):
        file_list = os.listdir(self.mainPath)
        print("ls %s"%self.mainPath)
        if not file_list:
            file_str = "<empty dir>"
        else:
            file_str = "\n".join(file_list)
        self.request.sendall(file_str.encode("utf-8"))

    def cd(self,**data):
        dir_name = data.get("dirname")
        print("cd %s\n"%dir_name)
        if dir_name == "..":
            self.mainPath = os.path.dirname(self.mainPath)
        else:
            self.mainPath = os.path.join(self.mainPath,dir_name)

        self.request.sendall(self.mainPath.encode("utf-8"))

    def mkdir(self,**data):
        dirname = data.get("dirname")
        path = os.path.join(self.mainPath,dirname)
        if not os.path.exists(path):
            if "/" in dirname:
                os.makedirs(path)
            else:
                os.mkdir(path)
            self.request.sendall("create success".encode("utf-8"))
        else:
            self.request.sendall("dirname exist".encode("utf-8"))


