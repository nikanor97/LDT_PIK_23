FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.3.1
ENV PYTHONPATH "${PYTHONPATH}:/code"

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /code
COPY . /code

RUN poetry config installer.max-workers 10
RUN poetry install --no-dev --no-interaction --no-ansi
