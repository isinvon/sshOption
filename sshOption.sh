#!/bin/bash

# 确保当前脚本和Python脚本在同一目录下
# 使用相对路径执行Python脚本
python3 "./sshOption.py"

# 为了让脚本执行完后暂停，以便查看输出或按任意键继续
read -p "Press any key to continue..."

# 或者，如果你不希望等待用户输入，直接让脚本执行完毕后退出
# echo "Script execution finished."