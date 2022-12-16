ARG IMAGE=python:alpine3.8

FROM $IMAGE as build-stage

ENV VIRTUAL_ENV=/app/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PYTHONUNBUFFERED 1
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apk update \
    && apk add --no-cache build-base gcc curl dpkg

RUN dpkg --add-architecture i386

WORKDIR /app
COPY . /app

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN pip3 install pyinstaller

RUN pyinstaller --onefile main.py --noconfirm --hiddenimport amqp --hiddenimport async-timeout --hiddenimport billiard --hiddenimport boto3 --hiddenimport botocore --hiddenimport cachetools --hiddenimport celery --hiddenimport certifi --hiddenimport charset-normalizer --hiddenimport click --hiddenimport click-didyoumean --hiddenimport click-plugins --hiddenimport click-repl --hiddenimport env-file --hiddenimport Flask --hiddenimport Flask-Cors --hiddenimport Flask-Log-Request-ID --hiddenimport google-auth --hiddenimport idna --hiddenimport importlib-metadata --hiddenimport itsdangerous --hiddenimport Jinja2 --hiddenimport jmespath --hiddenimport kombu --hiddenimport kubernetes --hiddenimport MarkupSafe --hiddenimport oauthlib --hiddenimport packaging --hiddenimport prompt-toolkit --hiddenimport pyasn1 --hiddenimport pyasn1-modules --hiddenimport pyparsing --hiddenimport python-dateutil --hiddenimport pytz --hiddenimport PyYAML --hiddenimport redis --hiddenimport requests --hiddenimport requests-oauthlib --hiddenimport rsa --hiddenimport s3transfer --hiddenimport six --hiddenimport urllib3 --hiddenimport values --hiddenimport vine --hiddenimport watchtower --hiddenimport wcwidth --hiddenimport websocket-client --hiddenimport Werkzeug --hiddenimport zipp --hiddenimport celery.fixups --hiddenimport celery.fixups.django --hiddenimport celery.apps.worker --hiddenimport celery.app.log --hiddenimport celery.app.amqp --hiddenimport kombu.transport.redis --hiddenimport celery.concurrency.prefork --hiddenimport celery.worker.components --hiddenimport celery.worker.autoscale --hiddenimport celery.worker.consumer --hiddenimport celery.app.control --hiddenimport celery.app.events --hiddenimport celery.events.state --hiddenimport celery.backends --hiddenimport celery.backends.redis --hiddenimport celery.worker.strategy --hiddenimport api.delete_session --hiddenimport api
RUN pyinstaller --onefile tasks.py --noconfirm --hiddenimport celery.fixups --hiddenimport celery.fixups.django --hiddenimport celery.apps.worker --hiddenimport celery.app.log --hiddenimport celery.app.amqp --hiddenimport kombu.transport.redis --hiddenimport celery.concurrency.prefork --hiddenimport celery.worker.components --hiddenimport celery.worker.autoscale --hiddenimport celery.worker.consumer --hiddenimport celery.app.control --hiddenimport celery.app.events --hiddenimport celery.events.state --hiddenimport celery.backends --hiddenimport celery.backends.redis --hiddenimport celery.worker.strategy

FROM $IMAGE

WORKDIR /app
COPY --from=build-stage /app/dist/ /app
COPY --from=build-stage /app/docker/entrypoint.sh /app

EXPOSE 5002

#CMD ["watch", "date"]
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
