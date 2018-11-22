#!/usr/bin/env sh

cd $(dirname "$0")/..
project_root=$(pwd)
echo "当前工作目录: $project_root"

export PYTHONPATH=$project_root/src:$PYTHONPATH
# 环境变量
export LOG_HEADER="export"

# 启动进程
exec python2 $project_root/src/auth/management/commands/mysql_dump.py -host mysql -P 3306 -u root -p 'root' -db guanjia -dir "$project_root/run/backup/"
