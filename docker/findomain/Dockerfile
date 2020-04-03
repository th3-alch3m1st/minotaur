FROM ubuntu:18.04

RUN apt-get update && apt-get install -y wget
RUN apt-get install -y python python-dev python-pip
RUN python -m pip install pika --upgrade

WORKDIR /tools
RUN mkdir -p /tools/input
RUN mkdir -p /tools/output

ADD ./consumer.py /tools/

RUN wget https://github.com/Edu4rdSHL/findomain/releases/latest/download/findomain-linux
RUN chmod +x findomain-linux

ENTRYPOINT ["python", "/tools/consumer.py", "findomain"]
