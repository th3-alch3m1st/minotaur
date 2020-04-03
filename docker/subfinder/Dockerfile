# Build Container
FROM golang:1.13.4-alpine3.10 AS build-env
MAINTAINER Ice3man (nizamul@projectdiscovery.io)
RUN apk add --no-cache --upgrade git openssh-client ca-certificates
RUN apk add --update bash python python-dev py-pip
RUN python -m pip install pika --upgrade
RUN go get -u github.com/golang/dep/cmd/dep
WORKDIR /go/src/app

# Cache the dependencies early - Changed from original
ADD ./Gopkg.toml ./Gopkg.lock ./
RUN dep ensure -vendor-only -v

# Install
RUN go get -u github.com/projectdiscovery/subfinder/cmd/subfinder

WORKDIR /tools
RUN mkdir -p /tools/input
RUN mkdir -p /tools/output

ADD ./consumer.py /tools/

ENTRYPOINT ["python", "/tools/consumer.py", "subfinder"]
