FROM python:2.7.12
MAINTAINER Alastair Paragas "alastairparagas@gmail.com"

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

VOLUME /neuroknight
EXPOSE 80
