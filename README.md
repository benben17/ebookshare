# ebookshare

## 对接微信公众号（支持个人公众号以及企业公众号）
使用公众号回复的方式进行搜书
## 安装所需依赖

```angular2html
pip3 install -r requirements.txt
```

## 启动
```
gunicorn app:app -b 127.0.0.1:8000
python3 app.py 
```
