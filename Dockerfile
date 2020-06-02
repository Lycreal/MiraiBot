FROM python:slim

ADD . /app/

RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    pip3 install --no-cache-dir -r /app/requirements.txt

WORKDIR /app/data

ENTRYPOINT ["python3", "run.py"]
