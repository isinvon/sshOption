# coding=utf-8
import sys
import logging


from paramiko.client import SSHClient, AutoAddPolicy
from paramiko import AuthenticationException
from paramiko.ssh_exception import NoValidConnectionsError


class SShClient:
    def __init__(self, host_ip, username, password):
        # 创建ssh对象
        self.ssh_client = SSHClient()
        self.host_ip = host_ip
        self.username = username
        self.password = password
        self.port = 22

    def __enter__(self):
        try:
            # 设置允许连接known_hosts文件中的主机（默认连接不在known_hosts文件中的主机会拒绝连接抛出SSHException）
            self.ssh_client.set_missing_host_key_policy(AutoAddPolicy)
            # 连接服务器
            self.ssh_client.connect(
                self.host_ip, self.port, self.username, self.password, timeout=60)
        except AuthenticationException as e:
            logging.warning('username or password error')
            raise e
            # return 1001
        except NoValidConnectionsError as e:
            logging.warning('connect time out')
            raise e
            # return 1002
        except Exception as a:
            print('Unexpected error:', sys.exc_info()[0])
            raise a
            # return 1003
        return self

    def excute_command(self, commands):
        # 执行命令
        # stdin：标准输入（就是你输入的命令）；stdout：标准输出（就是命令执行结果）；stderr:标准错误
        # （命令执行过程中如果出错了就把错误打到这里），stdout和stderr仅会输出一个
        stdin, stdout, stderr = self.ssh_client.exec_command(commands)
        # 返回命令结果
        return stdout.read().decode()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 关闭服务器连接
        self.ssh_client.close()

""" 
if __name__ == '__main__':
    with SShClient('192.168.1.6', 'lin', 'xxxxx') as ssh_c:
        blk = 'vdb'
        # command = "df -h | grep /dev/%s" % blk
        command = 'fish'
        result = ssh_c.excute_command(command)
        if len(result) == 0:
            mount_command = "mount /dev/%s /mnt" % blk
            mount_result = ssh_c.excute_command(mount_command)
            print(mount_result)

 """