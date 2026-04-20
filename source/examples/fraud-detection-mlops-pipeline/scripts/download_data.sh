#!/usr/bin/env bash
set -euo pipefail

DATA_DIR="${1:?Usage: $0 <data_dir>}"
RAW_DIR="${DATA_DIR}/raw"

mkdir -p "${RAW_DIR}"

echo "============================================"
echo "TabFormer Dataset Download"
echo "============================================"
echo ""
echo "The TabFormer dataset must be downloaded manually from IBM Box:"
echo "  https://ibm.ent.box.com/v/tabformer-data/folder/130747715605"
echo ""
echo "1. Download 'transactions.tgz' from the link above"
echo "2. Place it in: ${RAW_DIR}/"
echo "3. Run this script again to extract it"
echo ""

if [ -f "${RAW_DIR}/card_transaction.v1.csv" ]; then
    echo "Dataset already extracted at ${RAW_DIR}/card_transaction.v1.csv"
    wc -l "${RAW_DIR}/card_transaction.v1.csv"
    exit 0
fi

if [ -f "${RAW_DIR}/transactions.tgz" ]; then
    echo "Extracting transactions.tgz..."
    tar xzf "${RAW_DIR}/transactions.tgz" -C "${RAW_DIR}/"
    echo "Extracted to ${RAW_DIR}/card_transaction.v1.csv"
    wc -l "${RAW_DIR}/card_transaction.v1.csv"
else
    echo "transactions.tgz not found in ${RAW_DIR}/"
    echo "Please download it from the IBM Box link above."
    exit 1
fi
