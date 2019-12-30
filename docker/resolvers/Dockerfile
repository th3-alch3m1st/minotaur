FROM python:3-alpine
LABEL maintainer "th3_alchem1st"

WORKDIR /tools

RUN python -m pip install --upgrade pip
RUN apk add git && apk add bash
RUN apk add --update python-dev py-pip
RUN python -m pip install pika --upgrade
RUN git clone https://github.com/teknogeek/fresh.py

RUN cd fresh.py && pip3 install -r requirements.txt

RUN mkdir -p /tools/input
RUN mkdir -p /tools/output

ADD ./receive.py /tools/

# This is for the fresh.py script to run without errors

ENTRYPOINT ["python", "receive.py", "brute"]
