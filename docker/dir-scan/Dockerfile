FROM ubuntu:18.04

# https://github.com/jheise/ubuntu-golang/blob/master/Dockerfile

# Python and Ubuntu
RUN apt-get update
RUN apt-get install -y python3-dev python3-pip python python-dev python-pip
RUN apt-get install -y git openssh-client ca-certificates wget gcc
RUN python -m pip install pika --upgrade
RUN python -m pip install tldextract

# Golang
RUN wget -P /tmp https://dl.google.com/go/go1.15.5.linux-amd64.tar.gz
RUN tar -C /usr/local -xzf /tmp/go1.15.5.linux-amd64.tar.gz
RUN rm /tmp/go1.15.5.linux-amd64.tar.gz

ENV GOPATH /go
ENV PATH $GOPATH/bin:/usr/local/go/bin:$PATH
RUN mkdir -p "$GOPATH/src" "$GOPATH/bin" && chmod -R 777 "$GOPATH"

RUN go get -u github.com/ffuf/ffuf

WORKDIR /tools
RUN mkdir input
RUN mkdir output

ADD ./consumer.py .

RUN git clone https://github.com/maurosoria/dirsearch.git
RUN chmod +x dirsearch/dirsearch.py

WORKDIR /tools/dirsearch
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python", "/tools/consumer.py", "dir-scan"]
