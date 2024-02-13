import paramiko


class SSHClientWrapper:
    def __init__(self, hostname, port, username, password):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.client = None

    def connect(self):
        if self.client is None:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.hostname, self.port,
                                self.username, self.password)
            

    def execute_command(self, command):
        if self.client is None:
            raise Exception("SSH client is not connected")
        stdin, stdout, stderr = self.client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if error:
            print(f"Error occurred: {error}")
        return output
    

    def close(self):
        if self.client is not None:
            self.client.close()
            self.client = None


""" 使用示例 

# 创建SSH连接包装器实例
ssh_wrapper = SSHClientWrapper(
    "", 22, "root", "password")

# 建立SSH连接
ssh_wrapper.connect()

try:
    # 永久循环来执行命令
    while True:
        # 输入命令或从其他来源获取命令
        command = input("Enter a command to execute (or 'quit' to exit): ")

        # 检查用户是否输入了'quit'来退出循环
        if command.lower() == 'quit':
            break

        # 执行命令并打印输出
        output = ssh_wrapper.execute_command(command)
        print(f"Command output: {output}")

# try:
#     # 在同一个连接中执行无数个命令
#     # for i in range(10):  # 示例：执行10个命令
#     while True:
#         command = f"echo Command number {i}"
#         output = ssh_wrapper.execute_command(command)
#         print(f"Command {i} output: {output}")

#     # 您可以根据需要继续添加更多的命令
#     # ...

except Exception as e:
    # 处理任何异常
    print(f"An error occurred: {e}")

finally:
    # 确保连接总是被关闭
    ssh_wrapper.close()

"""