import subprocess


class CountServerChildFiles:
    """ 从本地利用ssh统计服务器上某个文件夹中的子文件数量 """

    def get_file_count_via_ssh(self, hostname, port, username, password=None, folder_path=''):
        """ 
        获取远程服务器上文件夹内的文件总数
        返回file_count:int """
        # 构建SSH命令
        
        command = [
            'ssh',
            f'-p {port}',
            f'{username}@{hostname}',
            f'sh -c "find {folder_path} -type f | wc -l"'
        ]

        # 如果使用密码认证，则需要使用pexpect或类似库来处理交互
        # 如果使用密钥认证，则不需要密码

        # 执行命令并获取输出
        # subprocess.run()执行完后立刻关闭连接
        result = subprocess.run(command, stdout=subprocess.PIPE, text=True)

        # 检查命令是否成功执行
        if result.returncode == 0:
            # 提取文件总数
            file_count = int(result.stdout.strip())
            return file_count
        else:
            # 命令执行失败，处理错误
            raise Exception("无法通过SSH检索文件数")

    
    
    def get_file_list_via_ssh(self,hostname, port, username, password=None, folder_path='.'):  
        """  
        获取远程服务器上文件夹内的文件列表,例如:['xxx.txt','lin.py','font.conf']（不包括子文件夹）  
        返回file_list:list  
        """  
        # 构建SSH命令，使用'find'命令来搜索文件并过滤掉目录  
        command = [  
            'ssh',  
            f'-p {port}',  
            f'{username}@{hostname}',  
            f'sh -c "find {folder_path} -type f"'  
        ]  
    
        # 执行命令并获取输出，显式设置编码为utf-8  
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')  
    
        # 检查命令是否成功执行  
        if result.returncode == 0:  
            # 提取文件列表，移除可能的空行和换行符  
            file_list = [line.strip() for line in result.stdout.split('\n') if line.strip()]  
            return file_list  
        else:  
            # 命令执行失败，处理错误  
            error_message = result.stderr.strip()  
            raise Exception(f"无法通过SSH检索文件列表: {error_message}")  
    
    # 获取要传输的文件列表，以计算总文件数  
    def get_file_list(self, folder, recursive=False):  
        """ 统计本地中文件夹内的文件总数,返回文件名列表,例如:[['xxx.txt','lin.py','font.conf']](不包括文件夹) """
        import os  
        file_list = []  
        for root, dirs, files in os.walk(folder):  
            if not recursive and root != folder:  
                break  
            file_list.extend(files)  
        # 返回数量可以用len(file_list)
        return file_list 
    
""" 测试用例
if __name__ == '__main__':
    c = CountServerChildFiles()
    # result = c.get_file_list_via_ssh(hostname='192.168.1.6',port=22,username='root',password='',folder_path='/home/lin/桌面/mycode')
    result = c.get_file_list(r'D:\PYproject\PyScript',recursive=True) # recursive就是是否递归到子文件夹中计数,一般都是Ture
    print(result)
"""