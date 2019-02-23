from socket import *
import os
import sys,time,signal

#文件库路径
FILE_PATH = "/home/tarena/ftpFile/"
HOST = ''
PORT = 8000
ADDR = (HOST,PORT)

#将文件服务器功能写在类中
class FtpServer(object):
    def __init__(self,connfd):
        self.connfd = connfd

    def do_list(self):
        #获取文件列表
        file_list = os.listdir(FILE_PATH)
        if not file_list:
            self.connfd.send("文件库为空".encode())
            return
        else:
            self.connfd.send(b"OK")
            time.sleep(0.1)

        files = ''
        for file in file_list:
            if file[0] != '.' and os.path.isfile(FILE_PATH + file):
                files = files + file + '#'
        self.connfd.sendall(files.encode())

    def do_send(self,filename):
        if filename not in os.listdir(FILE_PATH):
            self.connfd.send("未找到该文件".encode())
            return
        else:
            self.connfd.send(b'OK')
            time.sleep(0.1)
            file = FILE_PATH + filename
            with open(file,'rb') as f:
                while True:
                    line = f.readline()
                    if not line:
                        time.sleep(0.1)
                        self.connfd.send(b'end')
                        break
                    else:
                        self.connfd.send(line)
                print("文件发送完毕")

    def do_get(self,filename):
        with open(FILE_PATH+filename,'wb') as f:
            while True:
                content = self.connfd.recv(2048)
                if content.decode() == 'end':
                    break
                f.write(content)
            print("文件接收完毕")



#创建套接字，接收客户端连接，创建新的进程
def main():
    sockfd = socket()
    sockfd.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    sockfd.bind(ADDR)
    sockfd.listen(5)

    #处理子进程退出
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)
    print("Listening the port 8000...")

    while True:
        try:
            connfd,addr = sockfd.accept()
        except KeyboardInterrupt:
            sockfd.close()
            sys.exit("服务器退出")
        except Exception as e:
            print("服务器异常:",e)
            continue

        print("已连接客户端：",addr)
        #创建子进程
        pid = os.fork()
        if pid == 0:
            sockfd.close()
            ftp = FtpServer(connfd)
            #判断客户端请求
            while True:
                data = connfd.recv(1024).decode()
                if not data or data[0] == 'Q':
                    connfd.close()
                    sys.exit("客户端退出")
                elif data[0] == 'L':
                    ftp.do_list()
                elif data[0] == 'G':
                    filename = data.split()[-1]
                    ftp.do_send(filename)
                elif data[0] == 'P':
                    filename = data.split()[-1]
                    ftp.do_get(filename)

        else:
            connfd.close()
            continue


if __name__ == "__main__":
    main()
