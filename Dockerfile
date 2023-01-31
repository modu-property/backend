# pull official base image
FROM python:3.8-alpine

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1  # 디스크에 .pyc 파일 쓰기 방지함
ENV PYTHONUNBUFFERED 1  # 표준 출력, 표준 에러를 버퍼링하지 않음

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev py3-pip

# install python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install gunicorn
RUN python3.8 -m venv venv
RUN source venv/bin/activate
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY . .
