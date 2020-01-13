FROM ubuntu:16.04

WORKDIR /tools

RUN apt-get update
RUN apt-get install -y libldns-dev git build-essential
RUN apt-get install -y python python-dev python-pip
RUN python -m pip install pika --upgrade
RUN git clone https://github.com/blechschmidt/massdns.git

RUN cd massdns && make
RUN mv massdns/bin/massdns /bin/massdns

# Install fresh.py to remove known false positives of results
RUN apt-get install -y python3-dev python3-pip
RUN git clone https://github.com/teknogeek/fresh.py
RUN cd fresh.py && pip3 install -r requirements.txt
RUN cd fresh.py && chmod +x clean.sh

RUN mkdir -p /tools/input
RUN mkdir -p /tools/output

ADD ./consumer.py /tools/

ENTRYPOINT ["python", "consumer.py", "resolve"]
