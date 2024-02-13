import paramiko


class SSHConnectionTester:
    """ 测试SSH连接的可连通性 """

    def __init__(self, hostname, port=22, username=None, password=None, timeout=10):
        """ 其中timeout即设置超时时间,默认10s,因为ssh连接一般很快,如果慢那就是有问题了 """
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def test_connection(self):
        """ ssh测试连接,返回值类型为bool,连接成功返回ture """
        try:
            self.ssh_client.connect(self.hostname, port=self.port,
                                    username=self.username, password=self.password, timeout=self.timeout)
            return True
        except (paramiko.AuthenticationException, paramiko.SSHException, Exception) as e:
            # 忽略异常并返回False
            return False
        finally:
            # 关闭SSH连接
            self.ssh_client.close()



""" 
测试用例

def main():
    tester = SSHConnectionTester(
        hostname='192.168.1.6', username='lixxx', password='your_ssh_password_here')
    if tester.test_connection():
        print('经测试服务器可连接')
    else:
        print('经测试服务器无法连接')
if __name__ == '__main__':
    main()
 """