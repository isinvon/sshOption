from paramiko import SSHClient
from scp import SCPClient
import sys
from utils.CountServerChildFiles import CountServerChildFiles


class SCPClientWrapper:
    """ 
    基于SCPClient
    SCPClient封装包
    用于客户端上传和下载文件
    可显示ip,端口 和 传输百分比
    """
    # 传输时显示每个文件的百分比,并且不断输出
    # def upload_file(self, hostname, local_folder, remote_username, remote_path, recursive=False):
    #     """
    #     上传文件
    #     hostname:主机IP地址
    #     resursive|Boolean:是否递归目录,如果是上传一个文件以及他里面的子文件,就需要设置为Ture,默认False(需要大写)
    #     local_folder:本地文件或文件夹的路径
    #     remote_path:远程文件夹

    #     """
    #     ssh = SSHClient()
    #     ssh.load_system_host_keys()
    #     ssh.connect(hostname=hostname, username=remote_username)

    #     #定义打印文件当前完成百分比的进度回调
    #     def progress(filename, size, sent):
    #         sys.stdout.write("%s's progress: %.2f%%   \r" %
    #                          (filename, float(sent)/float(size)*100))

    #     # SCPCLient将paramiko传输和进度回调作为其参数。
    #     scp = SCPClient(ssh.get_transport(), progress=progress)

    #     #您还可以使用progress4，它添加了第四个参数来跟踪IP和端口
    #     #有助于多线程跟踪源代码
    #     def progress4(filename, size, sent, peername):
    #         # sys.stdout.write("(%s:%s) %s's progress: %.2f%%   \r" % (peername[0], peername[1], filename, float(sent)/float(size)*100))
    #         print(f"({peername[0]}:{peername[1]}) {filename} progress: {float(sent)/float(size)*100:.2f}%")
    #     scp = SCPClient(ssh.get_transport(), progress4=progress4)

    #     scp.put(files=local_folder, remote_path=remote_path, recursive=recursive)
    #     #现在应该正在打印您的put函数的当前进度。

    #     scp.close()
# ----------------------------------------------------------------
    # 也会显示百分比,并且是整个文件的传输百分比,只在终端显示一行,不会连续输出
    def upload_file(self, hostname, port, local_folder, remote_username, remote_path, recursive=False):
        """  
        上传文件  
        :param hostname: 主机IP地址  
        :param local_folder: 本地文件或文件夹的路径  
        :param remote_username: 远程用户名  
        :param remote_path: 远程文件夹  
        :param recursive: 是否递归目录, 默认False  
        """
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(hostname=hostname, username=remote_username)

        # 全局变量，用于追踪传输进度
        total_files = 0
        transferred_files = 0

        # 定义打印文件传输进度的回调
        def progress_callback(filename, size, sent):
            nonlocal total_files, transferred_files

            # 文件传输开始时，增加已传输文件数
            if sent == 0:
                transferred_files += 1
                return  # 避免在文件传输开始时打印进度

            # 计算并显示整体进度
            percentage = (transferred_files / total_files) * 100
            sys.stdout.write(f"\033[33m({hostname}:{port})传输进度： {percentage:.2f}%   \r\033[0m")
            sys.stdout.flush()  # 确保实时输出

        # 获取要传输的文件列表，以计算总文件数
        def get_file_list(folder, recursive=False):
            import os
            file_list = []
            for root, dirs, files in os.walk(folder):
                if not recursive and root != folder:
                    break
                file_list.extend(files)
            return file_list

        # 获取要传输的文件总数
        files_to_transfer = get_file_list(local_folder, recursive=recursive)
        total_files = len(files_to_transfer)

        # 创建SCPClient实例并传入进度回调函数
        scp = SCPClient(ssh.get_transport(), progress=progress_callback)

        
        # 上传文件或目录
        scp.put(files=local_folder, remote_path=remote_path, recursive=recursive)

        # 关闭SCPClient连接
        scp.close()

        # 文件传输全部完成后，打印最终进度
        print(f"\033[32m({hostname}:{port})传输完成： 100.00%\033[0m")

    def download_file(self, hostname, local_path, remote_username, remote_folder, recursive=True, port='22', password=None):
        """  
        下载文件  
        :param hostname: 主机IP地址  
        :param local_folder: 本地文件或文件夹的路径  
        :param remote_username: 远程用户名  
        :param remote_path: 远程文件夹  
        :param recursive: 是否递归目录, 默认Ture, 
        因为下载的有文件有文件夹,所以必须递归,故设置resursive为Ture
        """
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(hostname=hostname, username=remote_username)

        # 全局变量，用于追踪传输进度
        total_files = 0
        transferred_files = 0

        # 定义打印文件传输进度的回调
        def progress_callback(filename, size, sent):
            nonlocal total_files, transferred_files

            # 文件传输开始时，增加已传输文件数
            if sent == 0:
                transferred_files += 1
                return  # 避免在文件传输开始时打印进度

            # 计算并显示整体进度
            percentage = (transferred_files / total_files) * 100
            sys.stdout.write(f"\033[33m ({hostname}:{port})传输进度： {percentage:.2f}%   \r\033[0m")
            sys.stdout.flush()  # 确保实时输出

        # 获取要传输的文件列表，以计算总文件数
        files_to_transfer = CountServerChildFiles().get_file_list_via_ssh(hostname=hostname,
                                                                          port=port, username=remote_username, password=password, folder_path=remote_folder)
        # files_to_transfer = get_file_list(folder=remote_folder, recursive=recursive)
        total_files = len(files_to_transfer)

        # 创建SCPClient实例并传入进度回调函数
        scp = SCPClient(ssh.get_transport(), progress=progress_callback)

        # 下载文件或目录,
        # 因为下载的有文件有文件夹,所以必须递归,故设置resursive为Ture
        scp.get(local_path=local_path,
                remote_path=remote_folder, recursive=recursive)

        # 关闭SCPClient连接
        scp.close()

        # 文件传输全部完成后，打印最终进度
        print(f"\033[32m({hostname}:{port})传输完成： 100.00%\033[0m")


""" 使用示例:
# if __name__ == '__main__':
#     scp = SCPClientWrapper()
#     scp.upload_file(hostname='192.168.1.6',port='22',local_folder='D:\\软件\\AAA',remote_path='/home/lin/桌面/mycode/',remote_username='root',recursive=True) 
"""