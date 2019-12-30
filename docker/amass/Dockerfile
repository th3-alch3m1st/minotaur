FROM golang:1.13-alpine3.10 as build
RUN apk --no-cache add git
RUN go get github.com/OWASP/Amass; exit 0
ENV GO111MODULE on
WORKDIR /go/src/github.com/OWASP/Amass
RUN go install ./...

FROM alpine:latest
RUN apk --no-cache add ca-certificates
RUN apk add --update bash python python-dev py-pip
RUN python -m pip install pika --upgrade
COPY --from=build /go/bin/amass /bin/amass
COPY --from=build /go/src/github.com/OWASP/Amass/examples/wordlists/ /wordlists/
ENV HOME /

RUN mkdir -p /tools/input
RUN mkdir -p /tools/output
ADD ./receive.py /tools/

ENTRYPOINT ["python", "receive.py", "passive"]
