FROM golang:1.13-alpine3.10 as build
RUN apk add --no-cache --upgrade git openssh-client ca-certificates
RUN apk add bash

RUN go get -u github.com/tomnomnom/assetfinder

WORKDIR /tools
RUN mkdir -p /tools/input
RUN mkdir -p /tools/output

ADD ./start.sh /tools/
RUN chmod +x /tools/start.sh

ENTRYPOINT ["/tools/start.sh"]
