#!/bin/bash

# Usage: ./run_query_to_csv.sh my.sql my.csv
# Idea taken from: https://stackoverflow.com/a/11870348/345057
# Caveats:
#  column headers are lost
#  cannot escape the CSV delimiter when it appears as field value
# -> enough for a one-off including numerals, commit IDs, and filenames

DB='github'
USER='ma'

psql --no-align --tuples-only --field-separator=',' --dbname=$DB -U $USER --password <$1 >$2

