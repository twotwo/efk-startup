# Docker 封装的 Elasticsearch/Kibana/Filebeat 日志收集与展示方案

## EFK Geting Started

[Docker Compose](https://docs.fluentd.org/v/0.12/container-deployment/docker-compose) 部署 EFK+日志生产者，跑通日志收集、传输、存储到展示全流程

### 设置索引关联关系
登录 http://localhost:5601/
- Fluentd -> ES 的索引：fluentd-*
- Kibana：`Define index pattern` 设置成 `fluentd-*`

### 查看生产日志

`repeat 3 curl localhost:10080/`

![image](http://note.youdao.com/yws/res/573/AAF88487547E41CEA82237A4482AA29C)

### issue - docker logs 无法查看日志

```
(base) ➜  efk-demo docker logs -f efk-demo_web_1 
Error response from daemon: configured logging driver does not support reading
```

```
(base) ➜  efk-demo docker inspect -f '{{.HostConfig.LogConfig.Type}}' efk-demo_web_1 
fluentd
(base) ➜  efk-demo docker info --format '{{.LoggingDriver}}'
json-file
```

[Limitations of logging drivers](https://docs.docker.com/config/containers/logging/configure/#limitations-of-logging-drivers)

## Fluentd - Docker logging - 日志导出入门文档

[Docker Logging](https://www.fluentd.org/guides/recipes/docker-logging)

![Fluentd收集Docker容器日志](https://www.fluentd.org/assets/img/recipes/fluentd_docker.png)

### Start Docker container with Fluentd driver

![](https://www.fluentd.org/assets/img/recipes/fluentd_docker_integrated.png)


## 配置实践

### 在容器中的配置(最轻量级方案)

- [install-by-docker](https://docs.fluentd.org/v/0.12/container-deployment/install-by-docker)

[配置说明](https://docs.fluentd.org/v/0.12/configuration/config-file#list-of-directives)
1. `source` directives determine the input sources.
1. `match` directives determine the output destinations.
1. `filter` directives determine the event processing pipelines.
1. `system` directives set system wide configuration.
1. `label` directives group the output and filter for internal routing
1. `include` directives include other files.
