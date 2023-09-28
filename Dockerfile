FROM python:3.10 AS base

WORKDIR /app
ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

COPY pyproject.toml poetry.lock ./

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --verbose

FROM base AS app

WORKDIR /app
COPY . .

ENTRYPOINT ["uvicorn", "app.main:app", "--port", "8000"]