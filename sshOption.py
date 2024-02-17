import argparse
import os
# 获取当前脚本所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 改变当前工作目录到脚本所在目录
os.chdir(script_dir)
import re
import sys

import inquirer
import keyboard
import wcwidth
import yaml
# from inquirer.themes import GreenPassion # 修改inquirer选择器被选中块的背景色
# from InquirerPy.base.control import Choice 
# from InquirerPy.resolver import prompt 
# from InquirerPy.separator import Separator
# from InquirerPy.validator import NumberValidator
from utils.SCPClientWrapper import SCPClientWrapper
from utils.SSHConnectionTester import SSHConnectionTester
from utils.SSHKeyManager import SSHKeyManager

CONFIG_FILE = 'servers.yaml'


# 加载配置文件(字典类型)
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf8') as file:
            # 输出字典类型
            return yaml.safe_load(file)
    return {}


# 修改配置文件
def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf8',) as file:
        # 设置 default_flow_style 为 False 以使用块样式输出
        # 设置 encoding 为 'utf-8' 以确保文件以 UTF-8 编码保存
        # , default_flow_style=False
        yaml.dump(config, file, encoding='utf-8', allow_unicode=True)


def validate_input(prompt, regex_pattern, error_message):
    while True:
        user_input = input(prompt)
        if re.match(regex_pattern, user_input):
            return user_input
        else:
            print(error_message)


# 添加服务
def add_server():
    config = load_config()
    # name_regex = r'^[a-zA-Z0-9\-_]+$'  # 服务器名称的正则表达式小写字母（a-z）,大写字母（A-Z）,数字（0-9）,连字符（-）,下划线（_）

    while True:
        name = input("请自定义服务器的名称: ")
        if name in config:
            print(f"\033[31m服务器名称 '{name}' 已存在，详细信息如下：\033[0m")
            print(f"\033[31m{name} : {config[name]}\033[0m")
            continue
        # if not re.match(name_regex, name):
        #     print("服务器名称不符合规范，请重新输入！")
        #     continue
        break
    # 用户名只能是英文,数字或者两者组合
    user = validate_input('请输入登录的用户: ', r'^[a-zA-Z0-9\_]+$', "用户名不符合规范，请重新输入！")
    # IP地址只能是ipv4地址或者简单的英文域名,暂时不支持ipv6,因为维护难度大
    ip = validate_input(
        "请输入此服务器IP: ", r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])*\.)*[a-zA-Z]{2,}$', "IP地址不符合规范，请重新输入！")
    port = validate_input("请输入此服务器ssh端口: ",
                          r'^\d+$', "端口号不符合规范，请重新输入！")
    password = validate_input("请输入服务器的连接密码: ", r'.+', "密码不能为空，请重新输入！")

    config[name] = {'user': user, 'ip': ip, 'port': port, 'password': password}

    # 测试服务器连接性
    sshtest = SSHConnectionTester(hostname=ip, username=user, port=int(
        port), password=password, timeout=15).test_connection()

    # 如果可以连接
    if sshtest:
        print("\033[32m经测试服务器可以正常连接\033[0m")
        pass
    else:
        print("\033[31m经测试服务器无法连接，请确认服务器信息正确后重新添加\033[0m")
        return
    
    # 添加公钥到服务器中
    print('正在向服务器添加本机公钥...')
    SSHKeyManager(remote_host=ip, remote_port=int(
        port), username=user, password=password).add_public_key_to_remote_if_needed()
    print('正在将您输入的服务器配置进行保存...')
    save_config(config)
    print(f"\033[32m服务器 : {name} {config[name]} 已添加\033[0m")  # 红色输出



# 删除服务
def delete_server():
    config = load_config()
    servers = list(config.keys())
    if not servers:
        print("没有服务器可以删除")
        return
    choice = [
        inquirer.List(
            name='server',
            message='请选择你要删除的服务器,Enter执行',
            choices=servers,
            hints=config,
        ),
    ]

    name = inquirer.prompt(choice)['server']
    confirm = input(f"确认删除服务器 {name} 吗? (y/n) Enter默认y: ").strip().lower()
    if confirm == '' or confirm == 'y':
        del config[name]
        save_config(config)
        print(f"\033[32m服务器 {name} 已删除\033[0m")  # 绿色输出
    elif confirm == 'n':
        print('\033[91m已取消删除操作\033[0m')
        return


# 修改服务
def update_server():
    config = load_config()
    # []类型 eg: ['联想小主机', 'kkltan', 'lenovo', 'tttttt', '百度云', '腾讯云']
    servers = list(config.keys())
    if not servers:
        print("没有服务器可以修改")
        return
    # 选择要修改的服务器
    choice1 = [
        inquirer.List(
            name='servername',
            message='请选择你要修改的服务器,Enter执行',
            choices=servers,
            hints=config
        ),
    ]
    name1 = inquirer.prompt(choice1)
    name1 = name1['servername']
    # 获取服务器名为name1在servers中的下标
    name1_index = servers.index(name1)
    # 罗列服务器的子信息,并且上下键选择要删除的子信息
    choice2 = [
        inquirer.List(
            name='value',
            message='选择你要修改的信息',
            choices=config[name1],
            hints=config[name1]
        ),
        inquirer.Text(
            name='result',
            message=f'请输入修改后的值',
        )
    ]
    name2 = inquirer.prompt(choice2)
    value = name2['value']
    result = name2['result']
    update_info = {
        f'{value}': f'{result}',
    }
    config[name1].update(update_info)
    save_config(config)
    print(f'"{value}"修改成功,当前服务器"{name1}"的信息为:\n{config[name1]}')


# 罗列样式 1
# 罗列出所有的服务
def list_servers_1():
    config = load_config()
    servers = list(config.keys())
    if not servers:
        print("没有服务器")
        return
    text = f"\033[32mPlease select the server you want to login\033[0m"
    # 选择服务器列名
    choice = [
        inquirer.List(
            name='server',
            message="\033[32m"+text+"\033[0m",
            # eg: choices=['Jumbo', 'Large', 'Standard', 'Medium', 'Small', 'Micro'],
            choices=servers,
            hints=config
        ),
    ]
    # answer就是选项的名称,类型为list,因为还要存储子选项的名称
    answers = inquirer.prompt(choice)
    # 返回: ({'server': 'aliyun'}, {'user': 'lin', 'ip': '192.168.1.6', 'password': '***REMOVED***', 'port': 22})
    return answers, config[answers['server']]


# 罗列样式 2
# 罗列出所有的服务
def list_servers_2():
    config = load_config()
    servers = list(config.keys())
    if not servers:
        print("没有服务器")
        return
    # 服务器列名
    # text = f"{'server':<12}{'user':^10}{'ip':^30}{'port':^10}"
    template = "---------Please select the server you want to login---------"
    choice = [
        inquirer.List(
            name='server',
            message="\033[32m" + template + "\033[0m",
            # 完整的
            choices=list_servers_details(),
        ),
    ]
    # answer就是选项的名称,类型为list,因为还要存储子选项的名称
    answers = inquirer.prompt(choice)
    data = splic_server_info()
    # 查询选项对应的服务器信息
    for key, value in data.items():
        # 如果选项字符串 为 服务器子信息 的子集,说明查找成功, \u3000 即中文的空格
        if answers['server'].replace(' ', '').replace('\u3000', '') in str(key+data[key]):
            # 返回对应的服务器名称,以及查询到的子信息
            return key, config[key]
    return


# 拼接服务器的子信息
# 返回key-value字典,服务器名作为key,子信息作为value
def splic_server_info():
    config = load_config()  # 假设 load_config 函数已正确定义并返回所需的数据字典
    result = {}
    for name, info in config.items():
        # 按照指定格式拼接字符串
        key = name  # 服务器名
        value = '{user}{ip}{port}{password}'.format(
            user=info.get('user', ''),
            ip=info.get('ip', ''),
            port=str(info.get('port', '')),
            password=info.get('password', '')
        )
        # 移除空格并添加到结果字典中
        result[key] = value.replace(' ', '')
    # 返回结果字典
    # 返回格式: [ 'kkltan': 'root192.168.100.112212325434534', 'lenovo': 'sinvon192.168.1.122linxdasda']
    return result


# 罗列每条拼接过的服务信息
# 返回整个服务器的信息的拼接,包括服务器名,返回类型: list,一个服务器为一个元素,含有用于对齐的空格符
# 如 : ['    aliyun        lin       nav.sinvon.top       22    ', '    lenovo       sinvon      192.168.1.1         22    ']
def list_servers_details():
    result = []
    data = load_config()
    # 计算各个列的最大显示宽度, 修改 max_name_width、max_user_width 和 max_ip_width 可以增大减小列的宽度
    max_name_width = max(wcwidth.wcswidth(name) for name in data.keys())
    max_user_width = max(wcwidth.wcswidth(
        info['user']) for info in data.values())
    max_ip_width = max(wcwidth.wcswidth(info['ip']) for info in data.values())
    max_port_width = max(len(str(info['port']))
                         for info in data.values())  # 端口通常是数字，不需要考虑全角字符
    # 拼接成字符串，考虑中文宽度
    for name, info in data.items():
        formatted_line = (
            format_column(name, max_name_width+6, fill='^') +
            format_column(info['user'], max_user_width+10) +
            format_column(info['ip'], max_ip_width+10,) +
            format_column(str(info['port']),
                          max_port_width+10, fill='>')  # 端口右对齐
        )
        result.append(formatted_line)
    return result


# 解决中文不对齐
def format_column(value, width, fill=' '):
    # 计算需要的填充宽度
    fill_width = width - wcwidth.wcswidth(value)
    # 如果填充宽度为负（不应该发生），则设为0
    fill_width = max(0, fill_width)
    # 对于中文，我们使用全角空格作为填充字符
    if fill_width > 0 and any(u'\u4e00' <= ch <= u'\u9fff' for ch in value):
        fill = '\u3000' * (fill_width // wcwidth.wcwidth('\u3000'))
        # 如果需要的话，添加一个额外的半角空格来填补剩余的空间
        if fill_width % wcwidth.wcwidth('\u3000') != 0:
            fill += ' '
    else:
        fill = ' ' * fill_width
    return value + fill


# 加载配置文件(列表类型)
def load_config_to_list():
    result = []
    data = load_config()
    values_list = list(data.values())
    return values_list


# ssh连接服务器
def ssh_connect(server_info):
    user = server_info['user']
    ip = server_info['ip']
    port = server_info['port']
    password = server_info['password']
    cmd = f'ssh {user}@{ip} -p {port}'
    try:
        # 执行命令
        result_code = os.system(f'{cmd}'+' 2>&1')
        if result_code == 255:
            print(
                '\033[31m' + '-------ssh连接失败,请检查服务器信息是否正确后尝试重新连接--------' + '\033[0m')
    except Exception as e:
        print(f'SSH连接失败，错误信息:\n {e}')
    return


# 上传文件到服务器
def upload_file():
    """ 上传文件到服务器 """
    # 列出所有服务器,然后选择一个目标服务器
    config = load_config()
    servers = list(config.keys())
    if not servers:
        print('\033[31m' + '服务器列表为空，请先添加服务器' + '\033[0m')
        return
    choice = [
        inquirer.List(
            name='server',
            message='上传文件前请先选择服务器,Enter执行',
            choices=servers,
            hints=config,
        ),
    ]
    # 选择的服务器名
    name = inquirer.prompt(choice)['server']
    # 服务器的信息
    serverinfo = config[name]
    # 输入本地文件的路径,并且判断是否存在
    while True:
        local_folder = input('请输入本地上传的文件的路径: ')
        # 判断文件是否存在
        if os.path.exists(local_folder):
            break  # 如果文件存在，则跳出循环
        else:
            print('\033[31m' +
                  f'文件 {local_folder} 不存在，请重新输入。' + '\033[0m')
    local_folder = r"{}".format(local_folder)
    remote_folder = input('请输入保存到远程服务器端的路径: ')
    remote_ip = serverinfo['ip']
    remote_port = serverinfo['port']
    remote_username = serverinfo['user']
    local_folder_basename = os.path.basename(local_folder)
    try:
        print('正在上传文件...')
        # result_code = os.system(
        # #     # 本地打包并通过ssh传递给远程服务器上的tar命令解压
        # #     # f'tar -czf - {local_folder} | ssh {remote_username}@{remote_ip} "cd {remote_folder} && tar -xzvf -"')
        #     f'scp -C -P {remote_port} -r {local_folder} {remote_username}@{remote_ip}:{remote_folder}')
        # # f'tar -czf - --strip-components=1 {local_folder}/* | ssh {remote_username}@{remote_ip} "cd {remote_folder} && tar -xzvf -"')
        # if result_code == 0:
        #     print('\033[32m' + '所有文件上传完毕！' + '\033[0m')
        # else:
        SCPClientWrapper().upload_file(hostname=remote_ip, port=remote_port, local_folder=local_folder,
                                       remote_username=remote_username, remote_path=remote_folder, recursive=True)
    except Exception as e:
        print('\033[31m' + '文件上传失败，请确认服务器或路径信息正确后重新上传，报错信息为： {e}' + '\033[0m')


def download_file():
    """ 从服务器下载文件到本地 """
    # 列出所有服务器,然后选择一个目标服务器
    config = load_config()
    servers = list(config.keys())
    if not servers:
        print('\033[31m' + '服务器列表为空，请先添加服务器' + '\033[0m')
        return
    choice = [
        inquirer.List(
            name='server',
            message='下载文件前请先选择服务器,Enter执行',
            choices=servers,
            hints=config,
        ),
    ]
    # 选择的服务器名
    name = inquirer.prompt(choice)['server']
    # 服务器的信息
    serverinfo = config[name]
    # 输入本地文件的路径,并且判断是否存在
    while True:
        local_folder = input('请输入保存到本地的路径: ')
        # 判断文件是否存在
        if os.path.exists(local_folder):
            break  # 如果文件存在，则跳出循环
        else:
            print('\033[31m' +
                  f'文件 {local_folder} 不存在，请重新输入。' + '\033[0m')
    local_folder = r"{}".format(local_folder)
    remote_folder = input('请输入从远程服务器下载的文件的路径: ')
    remote_ip = serverinfo['ip']
    remote_port = serverinfo['port']
    remote_username = serverinfo['user']
    try:
        print('正在下载文件...')
        # result_code = os.system(
        #     # f'scp -P {remote_port} -r {remote_username}@{remote_ip}:{remote_folder} {local_folder}')
        #     f'scp -P {remote_port} {remote_username}@{remote_ip}:{remote_folder} {local_folder}')
        # if result_code != 0:
        #     print('\033[31m' + '文件下载失败，请确认服务器或路径信息正确后重新下载' + '\033[0m')
        # else:
        #     print('\033[32m' + '所有文件下载完毕！' + '\033[0m')
        SCPClientWrapper().download_file(hostname=remote_ip, local_path=local_folder, port=remote_port,
                                         remote_username=remote_username, remote_folder=remote_folder, recursive=True)
    except Exception as e:
        print('\033[31m' + '文件下载失败，请确认服务器或路径信息正确后重新下载，报错信息为： {e}' + '\033[0m')


# 主函数
def main():
    while True:
        print("""
        ----------------
        1. 列出服务器信息并选择连接
        2. 添加服务器信息
        3. 修改服务器信息
        4. 删除服务器信息
        5. 上传文件到服务器
        6. 从服务器下载文件
        7. 输出脚本所在路径
        8. 退出
        ----------------
        """)
        choice = input("请选择操作: ")
        if choice == '1':
            # 列出服务列表
            name, server_info = list_servers_2()
            if name:
                confirm = input(
                    f"确认连接服务器 {name} 吗? (y/n) Enter默认y: ").strip().lower()
                if confirm == '' or confirm == 'y':
                    print('正在连接到服务器...')
                    # 连接服务器
                    ssh_connect(server_info)
                elif confirm == 'n':
                    print("连接已取消")

        elif choice == '2':
            # 添加服务
            add_server()
        elif choice == '3':
            # 修改服务
            update_server()
        elif choice == '4':
            # 删除服务
            delete_server()
        elif choice == '5':
            # 从本地上传文件到服务器
            upload_file()
        elif choice == '6':
            # 从服务器下载文件到本地
            download_file()
        elif choice == '7':
            print(f"\033[32m脚本所在路径: {script_dir}\033[0m")
        elif choice == '8':
            print("退出程序")
            sys.exit(0)
        else:
            print("无效的选择，请重新输入")
        # 如果按下ECS键,就返回主界面
        if keyboard.is_pressed('esc'):
            main()
            
if __name__ == '__main__':
    main()
