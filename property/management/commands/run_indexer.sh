#!/bin/sh

docker exec -i manticore searchd --config /etc/manticoresearch/manticore.conf
docker exec -i manticore indexer --config /etc/manticoresearch/manticore.conf --all --rotate

mysql -P9306 -h0 -e "RELOAD TABLES"

exit 0
