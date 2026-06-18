#!/bin/bash

set -e

echo ""
echo "========================================="
echo " STOCK ANALYTICS PIPELINE "
echo "========================================="
echo ""

echo "Running Silver Layer..."
bash scripts/run_silver.sh

echo ""
echo "Running Gold Layer..."
bash scripts/run_gold.sh

echo ""
echo "========================================="
echo " PIPELINE COMPLETED SUCCESSFULLY "
echo "========================================="