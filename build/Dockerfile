FROM python:slim

ADD requirements.txt /root/

RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    pip3 install --no-cache-dir -r /root/requirements.txt && \
    rm /root/requirements.txt