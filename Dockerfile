FROM python:2.7.15-alpine3.6

# 一. 安装 linux package. (使用: 阿里云 alpine 镜像)
# 二. 安装 python package.
# 三. 清理不需保留的包 且 安装需保留的包.
ADD requirements /app/requirements/
RUN echo "http://mirrors.aliyun.com/alpine/v3.6/main/" > /etc/apk/repositories
RUN apk add --no-cache --virtual .build-deps \
    mariadb-dev build-base gcc python2-dev git linux-headers libffi-dev tzdata \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements/requirements.txt --trusted-host mirrors.aliyun.com --index-url http://mirrors.aliyun.com/pypi/simple \
    && apk del .build-deps \
    && apk add --no-cache mariadb-client-libs mariadb-client libstdc++ libffi

# WORKDIR: 如果目录不存在, 则自动创建
WORKDIR /app/src/
ADD src /app/src/

ADD bin /app/bin/

# docker-compose.yml 会覆盖 entrypoint
#ENTRYPOINT ["/app/bin/wxservice_deamon.sh"]
