#!/bin/bash

# ----------------------------------------------------------------------------------------------
# This script starts the garage door bot  application and logs the trace into a file
# ----------------------------------------------------------------------------------------------

# Change into the project root directory
SCRIPTDIR=$(readlink -f $(dirname "$0"))
pushd "${SCRIPTDIR}" > /dev/null
cd ..

./Common/scripts/showSW_Version.sh
python -u DoorStateUpdater.py 2>&1 | tee -a doorStateTrace.log
feedback=${PIPESTATUS[1]}

# Back to the original location
popd > /dev/null

exit ${feedback}
