FROM ubuntu:16.04

WORKDIR /tools

RUN apt-get update
RUN apt-get install -y libldns-dev git build-essential
RUN apt-get install -y python python-dev python-pip
RUN git clone https://github.com/blechschmidt/massdns.git

RUN cd massdns && make
RUN mv massdns/bin/massdns /bin/massdns

RUN mkdir -p /tools/input
RUN mkdir -p /tools/output

ADD ./receive.py /tools/

ENTRYPOINT ["python", "receive.py", "brute"]
