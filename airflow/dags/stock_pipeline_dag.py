from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    "owner": "ahamed",
    "depends_on_past": False
}

with DAG(
    dag_id="stock_pipeline",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="@hourly",
    catchup=False,
    tags=["stocks", "spark", "clickhouse"]
) as dag:

    silver_trade = BashOperator(
        task_id="silver_trade",
        bash_command="""
        docker exec spark-master \
        /spark/bin/spark-submit \
        /opt/spark/work-dir/silver_trade_processor.py
        """
    )

    silver_price = BashOperator(
        task_id="silver_price",
        bash_command="""
        docker exec spark-master \
        /spark/bin/spark-submit \
        /opt/spark/work-dir/silver_price_processor.py
        """
    )

    gold_symbol_summary = BashOperator(
        task_id="gold_symbol_summary",
        bash_command="""
        docker exec spark-master \
        /spark/bin/spark-submit \
        /opt/spark/work-dir/gold/gold_symbol_summary_builder.py
        """
    )

    gold_market_kpis = BashOperator(
        task_id="gold_market_kpis",
        bash_command="""
        docker exec spark-master \
        /spark/bin/spark-submit \
        /opt/spark/work-dir/gold/gold_market_kpis_builder.py
        """
    )

    gold_top_symbols = BashOperator(
        task_id="gold_top_symbols",
        bash_command="""
        docker exec spark-master \
        /spark/bin/spark-submit \
        /opt/spark/work-dir/gold/gold_top_symbols_builder.py
        """
    )

    gold_ohlc = BashOperator(
        task_id="gold_ohlc",
        bash_command="""
        docker exec spark-master \
        /spark/bin/spark-submit \
        /opt/spark/work-dir/gold/gold_ohlc_builder.py
        """
    )

    (
        silver_trade
        >> silver_price
        >> gold_symbol_summary
        >> gold_market_kpis
        >> gold_top_symbols
        >> gold_ohlc
    )