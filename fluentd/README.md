# Research on Fluentd

## First Container Demo

[Docker Image](https://docs.fluentd.org/v/0.12/container-deployment/install-by-docker)

```conf
# research/in_http.conf
<source>
  @type http
  port 10080
  bind 0.0.0.0
</source>
<match **>
  @type stdout
</match>
```

### Start Server

```bash
docker run --rm \
  -p 10080:10080 -v /opt/local/ide/workspaces/w2019/efk-demo/fluentd/research:/fluentd/etc -e FLUENTD_CONF=in_http.conf \
  fluent/fluentd
```

### Post Sample Logs via HTTP

```bash
curl -X POST http://localhost:10080/sample.test -d 'json={"json":"message"}'
```

## Export to ES

- [out_elasticsearch](https://docs.fluentd.org/output/elasticsearch)

## Export to RabbitMQ

- [Fluent All Plugins](https://www.fluentd.org/plugins/all) [fluent-plugin-rabbitmq](https://github.com/nttcom/fluent-plugin-rabbitmq)