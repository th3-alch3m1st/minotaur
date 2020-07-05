FROM python:3
RUN apt-get update -y
RUN apt-get install python3-pip -y
RUN apt-get install -y python python-dev python-pip
RUN python -m pip install pika --upgrade
RUN python -m pip install tldextract

WORKDIR /tools
RUN mkdir input
RUN mkdir output

ADD ./consumer.py .

RUN git clone https://github.com/maurosoria/dirsearch.git
RUN chmod +x dirsearch/dirsearch.py

ENTRYPOINT ["python", "/tools/consumer.py", "dir-scan"]
