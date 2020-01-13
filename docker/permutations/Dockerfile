FROM ubuntu:18.04
LABEL maintainer "th3_alchem1st"

WORKDIR /tools

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
    build-essential \
    ca-certificates \
    gcc \
    git \
    libpq-dev \
    make \
    python-pip \
    python2.7 \
    python2.7-dev \
    ssh \
    && apt-get autoremove \
    && apt-get clean

RUN apt-get install -y python3-pip python3-dev

RUN python -m pip install pika --upgrade
RUN pip3 install dnsgen

RUN mkdir -p /tools/input
RUN mkdir -p /tools/output

ADD ./consumer.py /tools/

ENTRYPOINT ["python2.7", "/tools/consumer.py", "permutations"]
