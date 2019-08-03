FROM python:3.7-alpine as base
FROM base as builder
# Install Packages
# https://www.elastic.co/guide/en/beats/filebeat/7.2/filebeat-installation.html
RUN mkdir /install
WORKDIR /install
ENV FILEBEAT_VERSION=7.2.0
RUN wget https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-${FILEBEAT_VERSION}-linux-x86_64.tar.gz && \
        tar xzvf filebeat-${FILEBEAT_VERSION}-linux-x86_64.tar.gz && \
        mkdir /install/bin  && \
        cp filebeat-${FILEBEAT_VERSION}-linux-x86_64/filebeat /install/bin && \
        mkdir -p /install/etc/filebeat &&\
        cp filebeat-${FILEBEAT_VERSION}-linux-x86_64/filebeat.yml /install/etc/filebeat/filebeat.example.yml  &&\
        rm -rf /install/filebeat-${FILEBEAT_VERSION}*
COPY requirements.txt /requirements.txt
RUN pip install --install-option="--prefix=/install"  -r /requirements.txt
FROM base
# Copy Builder Image
COPY --from=builder /install /usr/local
# Need by filebeat
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories  && \
        apk add --update --no-cache libc6-compat tzdata &&\
        ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
# Add alias
ENV ENV="/root/.ashrc"
RUN echo "alias ll='ls -l'" > "$ENV"

ARG AMQP_URI="amqp://guest:guest@rabbitmq/"
ENV AMQP_URI="${AMQP_URI}"

# needed to access all docker logs (read only) :
VOLUME /var/lib/docker/containers
# needed to access additional informations about containers:
VOLUME /var/run/docker.sock

COPY supervisord.conf /etc/
COPY modules.d /
COPY main.py logger_helper.py filebeat.docker.yml /

WORKDIR /
# Set Running Env by -e RABBITMQ_HOST=xxx ...

CMD ["supervisord", "--configuration", "/etc/supervisord.conf"]

