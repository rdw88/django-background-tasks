FROM python:3.9.2-buster

RUN mkdir /tasks

COPY requirements.txt /tasks
COPY requirements-test.txt /tasks
RUN pip install -r /tasks/requirements.txt
RUN pip install -r /tasks/requirements-test.txt

COPY . /tasks

WORKDIR /tasks
