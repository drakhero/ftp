from socket import *
import sys,time,os

filePath = '/home/tarena/clientFile/'

#基本文件操作功能
class FtpClient(object):
    def __init__(self,sockfd):
        self.sockfd = sockfd

    def do_list(self):
        self.sockfd.send(b"L")
        data = self.sockfd.recv(1024).decode()
        if data == 'OK':
            data = self.sockfd.recv(4096).decode()
            files = data.split('#')
            for file in files:
                print(file)
            print("文件列表展示完毕")
        else:
            print(data)

    def do_getFile(self,filename):
        file = 'G '+filename
        self.sockfd.send(file.encode())
        data = self.sockfd.recv(1024).decode()
        if data == 'OK':
            with open(filePath+filename,'wb') as f:
                while True:
                    line = self.sockfd.recv(2048)
                    if line == b'end':
                        break
                    else:
                        f.write(line)
                print("%s 下载完毕" % filename)
        else:
            print(data)

    def do_quit(self):
        self.sockfd.send(b'Q')

    def do_putFile(self,filename):
        file = 'P ' + filename
        self.sockfd.send(file.encode())
        time.sleep(0.1)
        with open(filePath+filename,'rb') as f:
            while True:
                content = f.read(2048)
                if not content:
                    time.sleep(0.1)
                    self.sockfd.send(b'end')
                    break
                self.sockfd.send(content)
            print("文件上传完毕")





#网络连接
def main():
    if len(sys.argv) < 3:
        print("argv is error")
        return
    HOST = sys.argv[1] #10.8.31.247
    PORT = int(sys.argv[2])
    ADDR = (HOST,PORT)

    sockfd = socket()

    try:
        sockfd.connect(ADDR)
    except:
        print("连接服务器失败")
        return
    ftp = FtpClient(sockfd)
    while True:
        print("========命令选项========")
        print("*********list**********")
        print("*********get file******")
        print("*********put file******")
        print("*********quit**********")
        print("=======================")

        cmd = input("请输入命令>>")
        if cmd.strip() == 'list':
            ftp.do_list()
        elif cmd.strip()[:3] == 'get':
            filename = cmd.split(' ')[-1]
            ftp.do_getFile(filename)
        elif cmd.strip() == 'quit':
            ftp.do_quit()
            sockfd.close()
            sys.exit("谢谢使用")
        elif cmd.strip()[:3] == 'put':
            filename = cmd.split(' ')[-1]
            if filename not in os.listdir(filePath):
                print("没有该文件")
                continue
            ftp.do_putFile(filename)
        else:
            print("请输入正确命令!!!")
            continue

if __name__ == "__main__":
    main()