本项目用来创建一个服务器，允许自定义生成日报。
## 如何使用

首先 clone 一个本仓库
```shell
git clone https://github.com/yichere/report-generator
```
然后使用 pip 安装依赖
```shell
pip install -r requirements.txt
```
最后使用 uvicorn 启动就大功告成了！
``` shell
uvicorn app:app --reload --port <port>
```
不加端口号时，默认开放端口为 8000
感谢您的使用！
## 贡献

本项目欢迎 pr！