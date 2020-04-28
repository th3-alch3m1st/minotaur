FROM alpine

WORKDIR tools
RUN apk update && apk add --no-cache libcap libpcap-dev
RUN apk add --no-cache --virtual .deps build-base linux-headers git clang clang-dev
RUN git clone --depth=1 --branch=master https://github.com/robertdavidgraham/masscan.git
RUN cd masscan && make && apk del .deps && rm -rf /var/cache/apk/*

RUN apk add nmap nmap-scripts && rm -rf /var/cache/apk/*
RUN apk add --update bash python python-dev py-pip
RUN python -m pip install pika --upgrade

RUN mkdir input
RUN mkdir output

ADD ./consumer.py /tools/

ENTRYPOINT ["python", "/tools/consumer.py", "ip-scan", "subnet-scan"]
