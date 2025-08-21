#!/usr/bin/env fish
# dump invenio stats indices using `elasticdump`
echo "=== Statistics indices ==="
curl -s "localhost:9200/_cat/indices?h=index" | grep stats
echo -e "\nThis script backs up the invenio-stats-file-download, invenio-events-stats-file-download, invenio-stats-record-view, invenio-events-stats-record-view, and invenio-stats-bookmarks indices; if you see others that need to be backed up above, the script needs to be modified. Note that there may be multiple aliases for these indices."

echo "Continue? (y/N)"
read confirmation
if [ "$confirmation" -ne y ]
    echo "Cancelled."
    exit 0
end

for idx in invenio-stats-file-download \
    invenio-events-stats-file-download \
    invenio-stats-record-view \
    invenio-events-stats-record-view \
    invenio-stats-bookmarks
    elasticdump --input http://localhost:9200/$idx --output $idx.mapping.json --type mapping
    elasticdump --input http://localhost:9200/$idx --output $idx.jsonl --type data
end

gzip invenio-*.json invenio-*.jsonl
and gsutil -m cp -n invenio-*.json.gz invenio-*.jsonl.gz gs://invenio-opensearch-index-backups/(date "+%Y-%m-%d")
# and rm invenio-*.json.gz

# to restore: https://inveniordm.docs.cern.ch/operate/ops/backup_search_indices/#restore
# elasticdump --input invenio-events-stats-record-view-*.mappings.json --output http://localhost:9200/(jq -r ". | keys[0]"  invenio-events-stats-record-view-*.mapping.json) --type mapping
# elasticdump --input invenio-events-stats-record-view-*.jsonl --output http://localhost:9200/(head -n1 invenio-events-stats-record-view-*.jsonl | jq -r "._index") --type data
