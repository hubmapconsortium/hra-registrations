#!/bin/bash

# Run normalization on all registrations.yaml files
for f in */registrations.yaml */*/registrations.yaml; do
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
