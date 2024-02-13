import os
# scp guide from https://www.runoob.com/linux/linux-comm-scp.html


class ScpCmdWrapper:
    """ 使用scp命令上传下载文件工具类,但是我使用这个工具类会卡死.... """

    def __init__(self, remote_username, remote_ip, remote_port):
        """ 初始化远程服务器的信息 """
        self.remote_username = remote_username
        self.remote_ip = remote_ip
        self.remote_port = remote_port

    def scp_upload_file_to_remote(self, local_folder, remote_folder):
        """ 上传'文件/文件夹'到服务器"""
        remote_username = self.remote_username
        remote_ip = self.remote_ip
        remote_port = self.remote_port
        # 无需添加报错信息,scp自带报错提示
        os.system(
            f'scp -P {remote_port} -r {local_folder} {remote_username}@{remote_ip}:{remote_folder}')

    def scp_download_file_from_remote(self, local_folder, remote_folder):
        """ 下载'文件/文件夹'到本地"""
        remote_username = self.remote_username
        remote_ip = self.remote_ip
        remote_port = self.remote_port
        os.system(
            f'scp -P {remote_port} -r {remote_username}@{remote_ip}:{remote_folder} {local_folder}')


# if __name__ == '__main__':
#     scp = ScpCmdWrapper()
#     scp.scp_download_file_from_remote(
#         remote_username='lin', remote_ip='192.168.1.6', remote_port='22', remote_folder='/home/lin/桌面/mycode/test.css', local_folder=r'D:\PYproject\PyScript\11ssh登录菜单选择脚本(版本1)\sshOption\test')
    # remote_folder = rf'D:\PYproject\PyScript\11ssh登录菜单选择脚本(版本1)\sshOption\test\click.py'
#     # local_folder = '/home/lin/桌面/mycode/'
#     # SCP(remote_username='lin', remote_ip='192.168.1.6', remote_port='22').scp_upload_file_to_remote(local_folder=local_folder,remote_folder=remote_folder)
