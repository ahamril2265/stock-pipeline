#!/bin/bash

set -e

echo "====================================="
echo "GOLD SYMBOL SUMMARY"
echo "====================================="

docker exec spark-master \
/spark/bin/spark-submit \
/opt/spark/work-dir/gold/gold_symbol_summary_builder.py

echo "====================================="
echo "GOLD MARKET KPIS"
echo "====================================="

docker exec spark-master \
/spark/bin/spark-submit \
/opt/spark/work-dir/gold/gold_market_kpis_builder.py

echo "====================================="
echo "GOLD TOP SYMBOLS"
echo "====================================="

docker exec spark-master \
/spark/bin/spark-submit \
/opt/spark/work-dir/gold/gold_top_symbols_builder.py

echo "====================================="
echo "GOLD OHLC"
echo "====================================="

docker exec spark-master \
/spark/bin/spark-submit \
/opt/spark/work-dir/gold/gold_ohlc_builder.py

echo "Gold Layer Complete"