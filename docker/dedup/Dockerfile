FROM golang:1.13-alpine3.10 as build
LABEL maintainer "th3_alchem1st"

WORKDIR /tools

RUN apk add --update bash python python-dev py-pip
RUN apk add --no-cache --upgrade git openssh-client ca-certificates
RUN go get -u github.com/tomnomnom/anew

RUN python -m pip install --upgrade pip
RUN python -m pip install pika --upgrade
RUN apk add bash

RUN mkdir -p /tools/input
RUN mkdir -p /tools/output

ADD ./consumer.py /tools/

ENTRYPOINT ["python", "/tools/consumer.py", "dedup"]
