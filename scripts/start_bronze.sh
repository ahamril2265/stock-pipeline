#!/bin/bash
set -e

exec /spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  --driver-memory 1G \
  --executor-memory 1G \
  --executor-cores 1 \
  --total-executor-cores 2 \
  --conf spark.sql.shuffle.partitions=8 \
  --conf spark.default.parallelism=4 \
  --packages \
org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,\
org.apache.spark:spark-avro_2.12:3.3.0,\
io.delta:delta-core_2.12:2.1.0,\
org.apache.hadoop:hadoop-aws:3.3.2,\
com.amazonaws:aws-java-sdk-bundle:1.12.262 \
/opt/spark/work-dir/unified_bronze_stream.py