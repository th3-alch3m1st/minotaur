FROM alpine

WORKDIR tools
RUN apk update && apk add --no-cache libcap libpcap-dev
RUN apk add --no-cache --virtual .deps build-base linux-headers git clang clang-dev
RUN git clone --depth=1 --branch=master https://github.com/robertdavidgraham/masscan.git
RUN cd masscan && make && apk del .deps && rm -rf /var/cache/apk/*
RUN mv /tools/masscan/bin/masscan /bin/

RUN apk add nmap nmap-scripts nmap-nselibs && rm -rf /var/cache/apk/*
RUN apk add --update bash python python-dev py-pip
RUN python -m pip install pika --upgrade
RUN python -m pip install netaddr

RUN mkdir input
RUN mkdir output

ADD ./consumer.py /tools/
ADD ./beefscan.sh /tools/
RUN chmod +x /tools/beefscan.sh

ENTRYPOINT ["python", "/tools/consumer.py", "ip-scan"]
