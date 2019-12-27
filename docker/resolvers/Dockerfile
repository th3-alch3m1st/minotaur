FROM python:3-alpine
LABEL maintainer "th3_alchem1st"

WORKDIR /tools

RUN python -m pip install --upgrade pip
RUN apk add git && apk add bash
RUN git clone https://github.com/teknogeek/fresh.py

RUN cd fresh.py && pip3 install -r requirements.txt

RUN mkdir -p /tools/input
RUN mkdir -p /tools/output

ADD ./start.sh /tools/
RUN chmod +x /tools/start.sh

# This is for the fresh.py script to run without errors
WORKDIR fresh.py

ENTRYPOINT ["/tools/start.sh"]
