#!/bin/bash

set -e

echo "====================================="
echo "RUNNING SILVER TRADE PROCESSOR"
echo "====================================="

docker exec spark-master \
/spark/bin/spark-submit \
/opt/spark/work-dir/silver_trade_processor.py

echo "====================================="
echo "RUNNING SILVER PRICE PROCESSOR"
echo "====================================="

docker exec spark-master \
/spark/bin/spark-submit \
/opt/spark/work-dir/silver_price_processor.py

echo "Silver Layer Complete"