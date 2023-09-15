FROM python:3.11.2-slim-bullseye

WORKDIR /

ENV PYTHONUNBUFFERED=1

ADD pyproject.toml .
ADD tarolog /tarolog
RUN mkdir /metrics

RUN pip install --upgrade pip wheel \
 && pip install -e '.'

CMD ["tarolog-bot"]
