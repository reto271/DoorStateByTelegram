#!/bin/bash

python DoorStateUpdater.py 2>&1 | tee -a doorState.log
