FROM golang:1.15-alpine as build
RUN apk add --no-cache --upgrade git openssh-client ca-certificates curl
RUN apk add --update bash python2 python2-dev
RUN curl -O https://bootstrap.pypa.io/get-pip.py && python get-pip.py
RUN python -m pip install pika --upgrade

RUN go get -u github.com/tomnomnom/httprobe
RUN GO111MODULE=on go get -u -v github.com/projectdiscovery/httpx/cmd/httpx
RUN GO111MODULE=on go get -u -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei

WORKDIR /tools
RUN mkdir -p /tools/input
RUN mkdir -p /tools/output

ADD ./consumer.py /tools/

ENTRYPOINT ["python", "/tools/consumer.py", "alive", "httpx", "nuclei"]
