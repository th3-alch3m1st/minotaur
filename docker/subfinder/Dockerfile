# Build Container
FROM golang:1.13.4-alpine3.10 AS build-env
MAINTAINER Ice3man (nizamul@projectdiscovery.io)
RUN apk add --no-cache --upgrade git openssh-client ca-certificates
RUN apk add bash
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

ADD ./start.sh /tools/
RUN chmod +x /tools/start.sh

ENTRYPOINT ["/tools/start.sh"]
