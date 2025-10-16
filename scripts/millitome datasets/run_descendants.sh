#!/bin/bash
# Run descendants script with logging
cd /Users/dequeue/Desktop/RUI.nosync/hra-registrations
python3 -u get_descendants_clean.py 2>&1 | tee descendants_output.txt
