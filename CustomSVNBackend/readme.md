# readme

## 制作虚拟环境

制作虚拟环境

## 安装依赖

```bash
python -m pip install -r requirements.txt
```

## 初始化数据库

```bash
python .\manage.py makemigrations
python .\manage.py migrate
```

## 创建超级用户

```bash
python .\manage.py createsuperuser
```

## 启动服务器

```bash
python .\manage.py runserver
```


## 创建数据库

### mysql

```
CREATE DATABASE IF NOT EXISTS CUSTOMSVN DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
```

## SVN数据上传客户端

### 各种需求

- 客户端只获取从自定义 SVN 服务器中现有最高 revision 开始的后续数据。
- 提供一个选项强制从 revision 1 开始更新所有数据。
- 用户可以指定更新某个区间的 SVN 数据。

## 使用nginx部署

```bash
python run_django.py
```

```


#user  nobody;
worker_processes  5;

#error_log  logs/error.log;
#error_log  logs/error.log  notice;
#error_log  logs/error.log  info;

#pid        logs/nginx.pid;


events {
    worker_connections  1024;
}


http {
    include       mime.types;
    default_type  application/octet-stream;

    #log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
    #                  '$status $body_bytes_sent "$http_referer" '
    #                  '"$http_user_agent" "$http_x_forwarded_for"';

    #access_log  logs/access.log  main;

    sendfile        on;
    #tcp_nopush     on;

    #keepalive_timeout  0;
    keepalive_timeout  65;
    client_max_body_size 20M;  # 允许最大 20MB 的上传

    #gzip  on;

    server {
        listen       80;
        server_name  QIAOYUANZHEN;

        #charset koi8-r;

        #access_log  logs/host.access.log  main;

        location / {
            root   D:/github/CustomSVN/CustomSVNFrontend/dist/;
            index  index.html index.htm;
            try_files $uri $uri/ /index.html;
        }

        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   html;
        }

        # # 如果没在前端的config.js中配置后端api的话需要在此配置后端api地址和端口
        # location = /config.js {
        #     add_header Content-Type application/javascript;
        #     return 200 'window.appConfig = { apiBaseUrl: "http://127.0.0.1:8000" };';
        # }

        location /static/ {
        alias D:/github/CustomSVN/CustomSVNBackend/static/;
        }
        location /media/ {
        alias D:/github/CustomSVN/CustomSVNBackend/media/;
        }

        location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        # 添加以下CORS相关头部
        add_header 'Access-Control-Allow-Origin' '*';
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS, PUT, DELETE';
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization';
        add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range';
        }
    }
 
}

```

Windows开启nginx

```bash
start ngnix
```

Windows开启关闭nginx

```bash
taskkill /F /IM nginx
```