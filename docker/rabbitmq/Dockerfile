FROM rabbitmq:3-management
RUN apt update
RUN apt install -y curl vim python-pip
RUN python -m pip install pika --upgrade

RUN mkdir -p /tools/input
RUN mkdir -p /tools/output
