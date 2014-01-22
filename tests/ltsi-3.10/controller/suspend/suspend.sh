#!/bin/sh
# scifab device driver autotest shell-script
# this program is run in /root. Please login /root with 'su' command

set -e
#set -x


BOARD_HOSTNAME="armadillo"
BOARD_USERNAME="root"
SCI_ID="1"
LOCAL_TTY="/dev/ttySC1"
# Run tty-ping.py to connect Host PC with the Board
$(dirname $0)/../common/suspend.py $BOARD_HOSTNAME $BOARD_USERNAME $SCI_ID $LOCAL_TTY

