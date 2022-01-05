# 写在最前面：强烈建议先阅读官方教程[Dockerfile最佳实践]（https://docs.docker.com/develop/develop-images/dockerfile_best-practices/）
# 选择构建用基础镜像（选择原则：在包含所有用到的依赖前提下尽可能提及小）。如需更换，请到[dockerhub官方仓库](https://hub.docker.com/_/golang?tab=tags)自行选择后替换。

# 选择基础镜像
FROM alpine:3.14
# 安装 python3
RUN apk add --no-cache python3 py3-pip  py3-setuptools python3-dev py3-lxml py3-requests py3-numpy py3-scipy py3-pandas py3-scikit-learn
RUN apk add --no-cache zlib-dev bzip2-dev pcre-dev openssl-dev ncurses-dev sqlite-dev readline-dev tk-dev
RUN apk add --no-cache gcc g++ make cmake
RUN rm -rf /var/cache/apk/*

# 拷贝当前项目到/app目录下
COPY . /app

# 设定当前的工作目录
WORKDIR /app

# 安装依赖到指定的/install文件夹
# 选用国内镜像源以提高下载速度
RUN pip config set global.index-url http://mirrors.cloud.tencent.com/pypi/simple \
&& pip config set global.trusted-host mirrors.cloud.tencent.com \
&& pip install --upgrade pip \
&& pip install setuptools \
&& pip  --exists-action=i --default-timeout=100 install asgiref==3.4.1 \
    sqlparse==0.4.2 \
    PyMySQL==1.0.2 \
    powerline-status==2.7 \
    joblib \
    jieba Django==3.2.8

# 设定对外端口
EXPOSE 80

# 设定启动命令
CMD ["python3", "manage.py", "runserver", "0.0.0.0:80"]
