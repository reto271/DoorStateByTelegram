#!/bin/bash

python -u DoorStateUpdater.py 2>&1 | tee -a doorState.log
