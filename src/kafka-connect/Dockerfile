FROM quay.io/strimzi/kafka:1.0.1-kafka-4.2.0
USER root:root
RUN mkdir -p /opt/kafka/plugins/s3-sink
COPY confluentinc-kafka-connect-s3-12.1.6/lib/* /opt/kafka/plugins/s3-sink/
USER 1001
