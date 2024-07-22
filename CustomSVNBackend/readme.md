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
server{
    listen  80;
    server_name  HOSTNAME;
    
    # 前端dist路径
    location / {
    root   D:/github/CustomSVN/CustomSVNFrontend/dist/;
    index  index.html index.htm;
    try_files $uri $uri/ /index.html;
    }
    
    # 后端地址:端口
    # 与后端运行的端口保持一致
    location /api/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    }
    
    # 后端静态文件目录
    location /static/ {
    alias DjangoProjectPath/static/;
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