FROM python:3.9-alpine

# set work directory
WORKDIR /modu_property

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1  # 디스크에 .pyc 파일 쓰기 방지함
ENV PYTHONUNBUFFERED 1  # 표준 출력, 표준 에러를 버퍼링하지 않음

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev libffi-dev binutils proj-dev geos gdal

# install python dependencies
COPY poetry.lock pyproject.toml /modu_property/
RUN pip install --upgrade pip
# RUN pip install wheel
# RUN pip install cffi
RUN pip install virtualenv
RUN python -m venv venv

RUN pip install poetry

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction

COPY . .
