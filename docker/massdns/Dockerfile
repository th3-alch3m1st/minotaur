FROM ubuntu:16.04

WORKDIR /tools

RUN apt-get update
RUN apt-get install -y libldns-dev git build-essential
RUN apt-get install -y python
RUN git clone https://github.com/blechschmidt/massdns.git

RUN cd massdns && make
RUN mv massdns/bin/massdns /bin/massdns

RUN mkdir -p /tools/input
RUN mkdir -p /tools/output

ADD ./start.sh /tools/
RUN chmod +x /tools/start.sh

ENTRYPOINT ["/tools/start.sh"]
