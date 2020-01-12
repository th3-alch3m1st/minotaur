FROM python:3-alpine
LABEL maintainer "th3_alchem1st"

WORKDIR /tools

RUN python -m pip install --upgrade pip
RUN python -m pip install pika --upgrade
RUN apk add git && apk add bash
RUN git clone https://github.com/teknogeek/fresh.py

RUN cd fresh.py && pip3 install -r requirements.txt

RUN mkdir -p /tools/input
RUN mkdir -p /tools/output

ADD ./receive.py /tools/

WORKDIR /tools/fresh.py

ENTRYPOINT ["python", "/tools/receive.py", "brute"]
