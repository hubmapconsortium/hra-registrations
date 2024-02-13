#!/bin/bash

SCRIPT=gen-registrations2.mjs
SHEET_ID=1ExZGB0NBLdmihaoDnsjdjwNHD2Lbii048bMkuAWQHbk
BASE=23-hbm-flagship

run() {
  echo "##" ${BASE}-$1
  echo https://hubmapconsortium.github.io/hra-registrations/${BASE}-${1}/
  echo
  echo

  mkdir -p ../${BASE}-$1
  cd ../${BASE}-$1
  node $SCRIPT $SHEET_ID $2
  if [ "$1" != 'all' ]; then
    cp ../${BASE}-all/index.html .
  fi

  echo
  echo
}

echo "# Report for ${BASE} papers"
echo

run all 0
run atkinson 1414155826
run hickey 505926750
run spraggins 234516829
run bluelake 1101416114
run ginty 285114166
