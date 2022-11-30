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
RUN pyinstaller --onefile main.py
#
#FROM $IMAGE
#
#WORKDIR /app
#COPY --from=build-stage /app/dist/ /app
#COPY --from=build-stage /app/docker/entrypoint.sh /app

EXPOSE 5002

CMD ["watch", "date"]
#RUN chmod +x entrypoint.sh
#ENTRYPOINT ["entrypoint.sh"]
