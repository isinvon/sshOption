import os
import paramiko

class SSHKeyManager:
    """ 
    我写的一个用来实现密钥连接的工具类, 能向远程主机添加本机的公钥,以实现无密码登录
    此工具类会判断本机是否有公钥,并且判断远程服务器是否已经存在本机公钥,如果存在就不会继续添加
    已经适配linux,unix,windows系统,放心食用 ! 
    """
    def __init__(self, remote_host, remote_port=22, username=None, password=None):
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.username = username
        self.password = password

    def get_local_public_key(self):
        """ 获取本机的公钥,适用linux,unix,windows """
        # 获取本地默认的 id_rsa.pub 等文件路径
        default_pubkey_files = ['~/.ssh/id_rsa.pub', '~/.ssh/id_ed25519.pub', '~/.ssh/id_ecdsa.pub']
        
        for pubkey_file in default_pubkey_files:
            expanded_path = os.path.expanduser(pubkey_file)
            
            if os.path.exists(expanded_path):
                with open(expanded_path, 'r') as f:
                    return f.read().strip()
        
        print("未找到默认的 SSH 公钥文件。")
        return None

    def check_remote_key(self, public_key):
        """ 检查远程服务器authorized_keys文件中是否已经存在本机的公钥 """
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            ssh_client.connect(hostname=self.remote_host,
                               port=self.remote_port,
                               username=self.username,
                               password=self.password)

            stdin, stdout, stderr = ssh_client.exec_command(f'grep -q "{public_key}" ~/.ssh/authorized_keys')
            exit_status = stdout.channel.recv_exit_status()
            
            ssh_client.close()

            return exit_status == 0  # 如果公钥已存在于远程，则返回True
        except Exception as e:
            print(f"检查远程服务器时发生错误: {e}")
            return False

    def add_public_key_to_remote_if_needed(self):
        """ 如果有需要的的就将公钥添加到远程主机,添加之前会判断是否已经存在本机公钥 """
        # 寻找本机公钥
        public_key = self.get_local_public_key()
        
        # 判断本机公钥是否找到了
        if public_key is not None and not self.check_remote_key(public_key):
            print('正在添加本机公钥到远程主机中...')
            try:
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                ssh_client.connect(hostname=self.remote_host,
                                   port=self.remote_port,
                                   username=self.username,
                                   password=self.password)

                commands = [
                    f'echo "{public_key}" >> ~/.ssh/authorized_keys',
                    'chmod 600 ~/.ssh/authorized_keys'
                ]

                for cmd in commands:
                    stdin, stdout, stderr = ssh_client.exec_command(cmd)
                    error_message = stderr.read().decode('utf-8').strip()
                    if error_message:
                        print(f"执行命令时发生错误: {cmd}\n错误详情：{error_message}")
                    else:
                        print(f"命令成功执行: {cmd}")

                ssh_client.close()
            except Exception as e:
                print(f"连接到服务器时发生错误: {e}")
        else:
            if public_key is None:
                print("未找到本地公钥文件。")
            elif self.check_remote_key(public_key):
                print("本机公钥已经存在于远程服务器上，无需再次添加。")



""" # 使用示例 
if __name__ == '__main__':
    ssh = SSHKeyManager(remote_host='192.168.11.92', remote_port=8022,username='u0_a211',password='xxxx').add_public_key_to_remote_if_needed()

 """