#!/bin/bash

time bash -c "time ./build.sh 2>&1" | tee log.txt
