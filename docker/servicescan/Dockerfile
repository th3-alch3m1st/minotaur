FROM alpine

WORKDIR tools
RUN apk update && apk add --no-cache libcap libpcap-dev
RUN apk add --no-cache nmap nmap-scripts nmap-nselibs && rm -rf /var/cache/apk/*

RUN apk add --update bash python python-dev py-pip
RUN python -m pip install pika --upgrade

RUN mkdir input
RUN mkdir output

ADD ./consumer.py /tools/

ENTRYPOINT ["python", "/tools/consumer.py", "service-scan"]
