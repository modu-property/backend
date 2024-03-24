#!/bin/sh
docker exec -i manticore indexer --config /etc/manticoresearch/manticore.conf --all --rotate

mysql -P9306 -hhost.docker.internal -e "RELOAD TABLES"
mysql -P9306 -hhost.docker.internal -e "RELOAD INDEXES"

exit 0
