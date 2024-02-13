import os  
import paramiko  
  
class SFTPUtil:  
    """ 基于SFTP的文件传输,支持上传和下载 """
    def __init__(self, hostname, port, username, password):  
        self.hostname = hostname  
        self.port = port  
        self.username = username  
        self.password = password  
        self.client = None  
  
    def connect(self):  
        try:  
            self.client = paramiko.SSHClient()  
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  
            self.client.connect(self.hostname, port=self.port, username=self.username, password=self.password)  
            self.sftp = self.client.open_sftp()  
            print("Connected to SFTP server successfully.")  
        except Exception as e:  
            print(f"Failed to connect to SFTP server: {e}")  
            self.client = None  
            self.sftp = None  
  
    def disconnect(self):  
        if self.sftp:  
            self.sftp.close()  
            self.sftp = None  
        if self.client:  
            self.client.close()  
            self.client = None  
        print("Disconnected from SFTP server.")  
  
    def create_dir(self, remote_dir):  
        try:  
            # Check if remote directory exists  
            if not self.sftp.stat(remote_dir):  
                print('This folder does not exist on the remote server, and is being created automatically. ...')
                # Create remote directory if it doesn't exist  
                self.sftp.mkdir(remote_dir)  
                print(f"Directory created on remote server: {remote_dir}")  
        except Exception as e:  
            print(f"Failed to create directory on remote server: {e}")  
  
    def sftp_put_file(self, local_dir, remote_dir):  
        try: 
            if os.path.isfile(local_dir):  
                # If local_dir is a file, upload it  
                self.sftp.put(local_dir, os.path.join(remote_dir, os.path.basename(local_dir)))  
                print(f"File uploaded successfully: {local_dir} -> {remote_dir}")  
            elif os.path.isdir(local_dir):  
                # If local_dir is a directory, recursively upload files and subdirectories  
                for root, dirs, files in os.walk(local_dir):  
                    for file in files:  
                        local_file_path = os.path.join(root, file)  
                        remote_file_path = os.path.join(remote_dir, os.path.relpath(local_file_path, local_dir))  
                        # Ensure remote directory exists before uploading file  
                        self.create_dir(os.path.dirname(remote_file_path))  
                        self.sftp.put(local_file_path, remote_file_path)  
                        print(f"File uploaded successfully: {local_file_path} -> {remote_file_path}")  
            else:  
                print(f"Invalid local path: {local_dir} is not a file or directory.")  
        except Exception as e:  
            print(f"Failed to upload file or directory: {e}")  
  
    def sftp_get_file(self, file, local_dir, remote_dir):  
        try:  
            # Ensure local directory exists before downloading file  
            os.makedirs(local_dir, exist_ok=True)  
            remote_file_path = os.path.join(remote_dir, file)  
            local_file_path = os.path.join(local_dir, file)  
            self.sftp.get(remote_file_path, local_file_path)  
            print(f"File downloaded successfully: {remote_file_path} -> {local_file_path}")  
        except Exception as e:  
            print(f"Failed to download file: {e}")  
            
            
"""             
 使用示例 
# 远程SFTP服务器的信息  
remote_ip = '192.168.1.6'  
remote_ssh_port = 22  
remote_username = 'root'  
remote_password = 'xxx'  
remote_dir = r'/home/lin/桌面/mycode'  
  
# 创建SFTPUtil实例并连接到服务器  
sftp_util = SFTPUtil(remote_ip, remote_ssh_port, remote_username, remote_password)  
if sftp_util.connect():  
    try:  
        # 本地目录，包含要上传的文件和目录  
        local_dir = r'D:\PYproject\PyScript\test\click.py'  
        # 调用sftp_put_file方法上传文件列表  
        # 注意：这里local_dir是文件/目录的根目录，而不是单个文件或目录  
        sftp_util.sftp_put_file(local_dir=local_dir,remote_dir=remote_dir)  
        
        print("All files and directories have been uploaded successfully.")  
    except Exception as e:  
        print(f"An error occurred during the upload process: {e}")  
    finally:  
        # 断开与SFTP服务器的连接  
        sftp_util.disconnect()
   """

        