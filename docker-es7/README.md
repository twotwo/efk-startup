# run ELASTIC on Docker

## Elasticsearch
- https://www.elastic.co/guide/en/elasticsearch/reference/7.x/docker.html

```yaml
    environment:
      - node.name=elasticsearch
      - cluster.name=docker-cluster
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
      - ELASTIC_PASSWORD=${ELASTIC_PASSWORD}
      - xpack.security.enabled=true
      - xpack.security.transport.ssl.enabled=true
      - network.host=0.0.0.0
      - cluster.initial_master_nodes=elasticsearch
```

## Kibana
- https://www.elastic.co/guide/en/kibana/7.x/docker.html
- https://www.elastic.co/guide/en/kibana/7.x/settings.html

```yaml
    environment:
      - I18N_LOCALE=zh-CN
      - ELASTICSEARCH_USERNAME=elastic
      - ELASTICSEARCH_PASSWORD=${ELASTIC_PASSWORD}
      - XPACK_GRAPH_ENABLED=true
      - TIMELION_ENABLED=true
      - XPACK_MONITORING_COLLECTION_ENABLED="true"
```