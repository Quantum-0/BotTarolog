FROM python:3.11.2-slim-bullseye

WORKDIR /

ADD pyproject.toml .
ADD tarolog /tarolog

RUN pip install --upgrade pip wheel \
 && pip install -e '.'

CMD ["tarolog-bot"]
