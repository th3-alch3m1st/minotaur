FROM golang:1.13-alpine3.10 as build

RUN apk add --no-cache --upgrade git openssh-client ca-certificates 
RUN apk add --update bash python python-dev py-pip
RUN python -m pip install pika --upgrade

WORKDIR /tools

RUN apk --update --no-cache add ldns 
RUN apk --no-cache --virtual .deps add ldns-dev build-base
RUN git clone https://github.com/blechschmidt/massdns.git

RUN cd massdns && make
RUN mv massdns/bin/massdns /usr/bin/massdns
RUN GO111MODULE=on go get -u -v github.com/projectdiscovery/shuffledns/cmd/shuffledns

RUN mkdir -p /tools/input
RUN mkdir -p /tools/output
ADD ./consumer.py /tools/

ENTRYPOINT ["python", "/tools/consumer.py", "wildcard"]
