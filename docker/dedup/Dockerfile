FROM python:2.7-alpine
LABEL maintainer "th3_alchem1st"

WORKDIR /tools

RUN python -m pip install --upgrade pip
RUN python -m pip install pika --upgrade
RUN apk add bash

RUN mkdir -p /tools/input
RUN mkdir -p /tools/output

ADD ./receive.py /tools/

ENTRYPOINT ["python", "/tools/receive.py", "dedup"]
