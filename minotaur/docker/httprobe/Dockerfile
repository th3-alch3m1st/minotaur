FROM golang:1.13-alpine3.10 as build
RUN apk add --no-cache --upgrade git openssh-client ca-certificates
RUN apk add --update bash python python-dev py-pip
RUN python -m pip install pika --upgrade

RUN go get -u github.com/tomnomnom/httprobe

WORKDIR /tools
RUN mkdir -p /tools/input
RUN mkdir -p /tools/output

ADD ./receive.py /tools/

ENTRYPOINT ["python", "receive.py", "alive"]
