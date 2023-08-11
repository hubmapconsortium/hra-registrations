#!/bin/bash
set -e

DIR=$1
RUI_LOCATIONS=$DIR/rui_locations.jsonld

echo $1

perl -pe 's/\/hubmap-ontology\//\/ccf-ontology\//g;s/ccf-entity-context/ccf-context/g;' $RUI_LOCATIONS | \
jsonld canonize | \
perl -pe 's/\/hubmap-ontology\//\/ccf-ontology\//g' | \
rdfpipe -i nquads -o turtle - --ns=dct=http://purl.org/dc/terms/ --ns=ccf=http://purl.org/ccf/ > $DIR/graph.ttl

comunica-sparql-file $DIR/graph.ttl -f scripts/dataset-report.rq -t text/csv > $DIR/report.csv
