#!/usr/env/bin sh

# 密码 root
mysql -h 127.0.0.1 -P 33333 -u root --password  < ../migrations/guanjia.sql  

#mysqlimport -h 127.0.0.1 -P 33333 -u root --password --ignore-lines=1 guanjia ../migrations/guanjia.sql --local
