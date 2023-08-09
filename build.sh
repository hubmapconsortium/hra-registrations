#!/bin/bash

for f in */registrations.yaml */*/registrations.yaml; do
  npx github:hubmapconsortium/hra-rui-locations-processor normalize `dirname $f`
done
