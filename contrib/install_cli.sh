 #!/usr/bin/env bash

 # Execute this file to install the nald cli tools into your path on OS X

 CURRENT_LOC="$( cd "$(dirname "$0")" ; pwd -P )"
 LOCATION=${CURRENT_LOC%Naldcoin-Qt.app*}

 # Ensure that the directory to symlink to exists
 sudo mkdir -p /usr/local/bin

 # Create symlinks to the cli tools
 sudo ln -s ${LOCATION}/Naldcoin-Qt.app/Contents/MacOS/naldd /usr/local/bin/naldd
 sudo ln -s ${LOCATION}/Naldcoin-Qt.app/Contents/MacOS/nald-cli /usr/local/bin/nald-cli
