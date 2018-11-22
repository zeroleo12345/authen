
### 开发环境

- CentOS 安装环境
``` bash
sudo yum install zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel xz xz-devel libffi-devel mysql-devel python-devel
pyenv install 2.7.15

```


## 启动充值系统步骤

- 主程序
``` bash
1. 修改配置
  - decrypt .env.x
  - direnv allow .
  - 修改.env   (原则: 尽量不用修改docker-compose.yml)

2. 构建 docker
  - docker-compose build --no-cache

3. 运行 docker
  - docker-compose up -d mysql
  Debug 版本:   export ENVIRONMENT=unittest; export DEBUG=True; docker-compose up auth
  Release 版本: export ENVIRONMENT=production; export DEBUG=False; docker-compose up auth

```


## 连接MySQL
``` bash
pip install mycli
mycli -h 127.0.0.1 -P 33333 -u root --password=root -D guanjia
```


### 其他
直接把exe或者apk, 放到/root/code/baicai/wxservice/static/js/目录, 浏览器访问: 114.115.148.148/js/1.exe  即可下载
