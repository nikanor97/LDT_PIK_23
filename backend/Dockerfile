#FROM ubuntu
#
## RUN add-apt-repository --yes ppa:deadsnakes/ppa && apt-get update --yes --quiet
## RUN #DEBIAN_FRONTEND=noninteractive apt-get install --yes --quiet --no-install-recommends \
##    python3.10 \
##    python3.10-dev \
##    python3.10-distutils \
##    python3.10-lib2to3 \
##    python3.10-gdbm \
##    python3.10-tk \
##    pip
#
#RUN apt-get update
#RUN apt-get install -y python3.10
#RUN apt-get install -y pip

FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.3.1
ENV PYTHONPATH "${PYTHONPATH}:/code"

RUN pip install "poetry==$POETRY_VERSION"
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 libgl1-mesa-dev xvfb -y

WORKDIR /code
COPY pyproject.toml ./pyproject.toml
RUN poetry install --only main --no-interaction --no-ansi

COPY . /code
RUN poetry config installer.max-workers 10
