FROM rabbitmq:3-management
RUN apt-get update
RUN apt-get install -y curl vim python-pip
RUN python -m pip install pika --upgrade

RUN mkdir -p /tools/input
RUN mkdir -p /tools/output

EXPOSE 5672 15672
