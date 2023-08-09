#!/bin/bash

for f in */registrations.yaml */*/registrations.yaml; do
  if [ "$1" == "local" ]; then
    node ../hra-rui-locations-processor/src/cli.js normalize `dirname $f`
  else
    npx github:hubmapconsortium/hra-rui-locations-processor normalize `dirname $f`
  fi
done
