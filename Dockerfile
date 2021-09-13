FROM python:alpine
COPY . /app
WORKDIR /app

RUN apk add py3-virtualenv

ENV VIRTUAL_ENV=/app/venv
RUN [ "/usr/local/bin/python", "-m", "venv", "$VIRTUAL_ENV"]
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install flask waitress
ENV FLASK_APP=tracker
RUN flask init-db

EXPOSE 8080
#ENTRYPOINT [ "python" ]
CMD [ "waitress-serve", "--call", "tracker:create_app" ]
