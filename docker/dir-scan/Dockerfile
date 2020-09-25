FROM golang:1.13-alpine3.10 as build
RUN apk add --no-cache --upgrade git openssh-client ca-certificates
RUN apk add --update bash python python3 py3-pip python-dev py-pip
RUN python -m pip install pika --upgrade
RUN python -m pip install tldextract

RUN go get -u github.com/ffuf/ffuf

WORKDIR /tools
RUN mkdir input
RUN mkdir output

ADD ./consumer.py .

RUN git clone https://github.com/maurosoria/dirsearch.git
RUN chmod +x dirsearch/dirsearch.py

ENTRYPOINT ["python", "/tools/consumer.py", "dir-scan"]
