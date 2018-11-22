#!/usr/bin/env sh

cd $(dirname "$0")/..
project_root=$(pwd)
echo "当前工作目录: $project_root"

export PYTHONPATH=$project_root/src:$PYTHONPATH
# 环境变量
export LOG_HEADER="auth"
export WEB_CONFIG=$project_root/etc/web.conf

# crond job
cp /app/bin/cron_jobs  /etc/crontabs/root
crond

# 启动进程
exec gunicorn -c $project_root/etc/gunicorn.conf -b '0.0.0.0:8001' auth.auth_server:app
