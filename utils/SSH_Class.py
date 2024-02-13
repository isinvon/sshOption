import paramiko
from time import sleep
 
class SSH_Class:
    hostIP = '192.168.0.2'
    TCP_Port = 22
    userName = 'root'
    passWord = 'root'
    keyFilePath = ''
    keyFilePassword = ''
    timeOut = 60
    def __init__(self, hostIP='', TCP_Port=22, userName='', passWord='', keyFilePath='', keyFilePassword='', timeOut=60, commands=[]):
        """初始化SSH_Class,参数赋初值可缺省"""
        self.hostIP = hostIP
        self.TCP_Port = TCP_Port
        self.userName = userName
        self.passWord = passWord
        self.keyFilePath = keyFilePath
        self.keyFilePassword = keyFilePassword
        self.timeOut = timeOut
        self.commands = commands
    def getSshObject(self):
        """创建SSH对象，用于SSH连接使用，并返回SSH paramiko对象"""
        ssh_Object = paramiko.SSHClient()
        ssh_Object.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if ssh_Object:
            return ssh_Object
        else:
            self.closeSshObject(ssh_Object)
    def connectByKey(self):
        """通过密钥进行SSH连接方法，返回SSH的连接对象"""
        if self.keyFilePassword:
            RSA_Key = paramiko.RSAKey.from_private_key_file(self.keyFilePath,password=self.keyFilePassword)
        else :
            RSA_Key = paramiko.RSAKey.from_private_key_file(self.keyFilePath)
        ssh_Object = self.getSshObject()
        ssh_Object.connect(hostname=self.hostIP,port=self.TCP_Port,username=self.userName,pkey=RSA_Key,timeout=self.timeOut)
        if ssh_Object:
            return ssh_Object
        else:
            self.closeSshObject(ssh_Object)
            raise Exception("The SSH Key Connection Failed!")
    def connectByPassword(self):
        """通过密码进行SSH连接方法，返回SSH的连接对象"""
        ssh_Object = self.getSshObject()
        ssh_Object.connect(hostname=self.hostIP,port=self.TCP_Port,username=self.userName,password=self.passWord,timeout=self.timeOut)
        if ssh_Object:
            return ssh_Object
        else :
            self.closeSshObject(ssh_Object)
            raise Exception("The SSH Password Connection Failed!")
    def closeSshObject(self, ssh_Object):
        """关闭SSH连接对象"""
        if ssh_Object:
            ssh_Object.close()
        else:
            raise Exception("Failed To Close SSH Connection!")
    def executeSshCommands(self, ssh_Object, My_Commands):
        """连接完成后执行命令，使用时具体细节请参照实际连接过程及命令执行过程"""
        result = ''
        if My_Commands:
            command = ssh_Object.invoke_shell()
            for com in My_Commands:
                sleep(1)
                command.send(com)
                out = command.recv(1024)
                #print(out.decode())
                result=result+(out.decode())
            return result
        else :
            self.closeSshObject(ssh_Object)
            raise Exception("No Commands are Executed!") 
 
 
"""  连接示例

if __name__ == '__main__':
    # My_Commands=['\n','\n','ls','\n','\n']
    My_Commands=['\n','\n','ls','\n','\n']
    #使用hostIP='192.168.0.2'传参可进行缺省参数传参
    sshClass = SSH_Class(hostIP='xx.xx.xx.xx', userName='root', passWord='password')
    sshObject = sshClass.connectByPassword()
    res = sshClass.executeSshCommands(sshObject,My_Commands)
    sshClass.closeSshObject(sshObject)
    print(res)
"""