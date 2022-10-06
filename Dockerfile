FROM python:alpine3.8

ENV VIRTUAL_ENV=/app/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app
COPY . /app/

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

EXPOSE 5002

RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
