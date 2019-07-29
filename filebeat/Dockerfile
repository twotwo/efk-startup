FROM python:3.7-alpine as base
FROM base as builder
# Install Packages
# https://www.elastic.co/guide/en/beats/filebeat/7.2/filebeat-installation.html
# RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories
# RUN apk add --update --no-cache libc6-compat
RUN mkdir /install
WORKDIR /install
ENV FILEBEAT_VERSION=7.2.0
RUN wget https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-${FILEBEAT_VERSION}-linux-x86_64.tar.gz && \
        tar xzvf filebeat-${FILEBEAT_VERSION}-linux-x86_64.tar.gz && \
        cp filebeat-${FILEBEAT_VERSION}-linux-x86_64/filebeat /usr/bin && \
        mkdir -p /etc/filebeat &&\
        cp filebeat-${FILEBEAT_VERSION}-linux-x86_64/filebeat.yml /etc/filebeat/filebeat.example.yml
COPY requirements.txt /requirements.txt
RUN pip install --install-option="--prefix=/install"  -r /requirements.txt
FROM base
# Copy Builder Image
COPY --from=builder /install /usr/local
# Add alias
ENV ENV="/root/.ashrc"
RUN echo "alias ll='ls -l'" > "$ENV"

ADD supervisord.conf /etc/

WORKDIR /

# CMD python rabbit2es.py
# ENTRYPOINT ["supervisord", "--configuration", "/etc/supervisord.conf"]

