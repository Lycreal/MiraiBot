FROM python:slim

ADD requirements.txt /root/

RUN pip3 install --no-cache-dir -r /root/requirements.txt && \
    rm /root/requirements.txt