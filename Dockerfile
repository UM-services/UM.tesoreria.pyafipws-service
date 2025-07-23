FROM python:3.13-alpine

WORKDIR /app

COPY requirements.txt ./

RUN apk update && apk add bash build-base git libffi-dev
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install git+https://github.com/dqmdz/pyafipws.git@v2025.05.05#egg=pyafipws

COPY . .

# Copia los archivos secretos
COPY user.crt user.crt
COPY user.key user.key

ENV FLASK_APP=app.service
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=${INSTANCE_PORT:-5000}
ENV FLASK_DEBUG=1
ENV FLASK_ENV=development

CMD ["sh", "-c", "flask run --host=0.0.0.0 --port=${INSTANCE_PORT:-5000} --debug"]