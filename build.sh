#!/bin/bash

# Run normalization on all registrations.yaml files
for f in */registrations.yaml */*/registrations.yaml; do
  echo $(dirname $f)
  if [ "$1" == "local" ]; then
    node ../hra-rui-locations-processor/src/cli.js normalize `dirname $f`
  else
    npx github:hubmapconsortium/hra-rui-locations-processor normalize `dirname $f`
  fi
done

# Update README.md with all official hra registration sets
head -3 README.md > TEMP; cat TEMP > README.md; rm -f TEMP;
echo >> README.md
echo "## Hosted Registration Sets:" >> README.md
echo >> README.md

for f in */registrations.yaml; do
  echo "* [$(dirname $f)](https://hubmapconsortium.github.io/hra-registrations/$(dirname $f)/)" >> README.md   
done

# Only run report generator if pre-requisites installed
if [ `which comunica-sparql-file` ]; then
  for f in */rui_locations.jsonld */*/rui_locations.jsonld; do
    ./scripts/report.sh `dirname $f`
  done
  
  npm run merge-reports
fi
