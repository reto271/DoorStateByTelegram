#!/bin/bash
rm -rf test-reports
python -m unittest discover -s . -p 'Test_*.py'
