#!/usr/bin/python

# suspend.py
#
# Simple test for PM over a ssh and wakeup via a serial port using wakeup.py

import getopt
import subprocess
import sys
import time

verbose = False

def info (str):
    if verbose:
        print str
    pass

class Test:
#Start a Test class
    def __init__(self, board_hostname, board_username, sci_id, board_tty):
        self.board_hostname = board_hostname
        self.board_username = board_username
	self.sci_id = sci_id
        self.board_tty = board_tty

#Call subprocess to send command
    def call_cmd(self, info_str, cmd):
        info(info_str)
	run_cmd = subprocess.call(cmd)
	return run_cmd

# arguments to access to board via ssh:
    def board_cmd_args(self, cmd):
        return ['ssh',self.board_username + '@' + self.board_hostname ] + cmd

# setting command with given arguments
    def base_cmd_args(self, setcmd):
        return [ '/bin/echo', setcmd, '>' ]

    def set_cmd_args(self, info_str, setcmd):
        cmd = self.base_cmd_args(setcmd)
	if setcmd == 'enabled':
	    cmd.append('/sys/devices/platform/sh-sci.' + str(self.sci_id) + \
                       '/tty/ttySC' + str(self.sci_id) +'/power/wakeup')
	elif setcmd == 'mem':
            cmd.append('/sys/power/state')
	else:
            print 'Unknown this command'
        return cmd

#Preparing a command before called
    def prepare_cmd(self, cmd):
	return [ ' '.join(cmd) ]

    def run_one(self, setcmd):

	if setcmd == 'enabled':
		info_str = 'setting cmd to wakeup device'
	elif setcmd == 'mem':
		print "Current progress suspending system..."
		info_str = 'Suspending system'
	else:
		print "Unknown value:%s" % (setcmd)

	param_str = self.prepare_cmd(self.set_cmd_args(info_str, setcmd))
	cal_cmd = self.call_cmd(info_str, self.board_cmd_args(param_str))
	
	return cal_cmd

# Running:
    def run(self):
        status = True
	# Setting the wakeup device and suspend system 
        for setcmd in [ 'enabled', 'mem' ]:
		retval = self.run_one(setcmd)
		if setcmd == 'enabled':
			if (retval == 0):
				print "Setting the wakeup device successfully!"
			else:
				print "Setting the wakeup device Failed!"
				status = False
		elif setcmd == 'mem':
			if (retval == 0):
				print "Suspending successfully!"
			else:
				print "Suspending Failed!"
                		status = False
		else:
			status = False

		time.sleep(1)
        return status

# Help
def usage():
        fatal_err(
"Usage: suspend.py [options] BOARD_HOSTNAME \\\n" +
"                       BOARD_USERNAME BOARD_TTY SCI_ID\\\n" +
"  where:\n" +
"\n"
"    BOARD_HOSTNAME:  Is the hostname of the board to connect to\n" +
"    BOARD_USERNAME:  Is the username to use when when loging into the board\n" +
"    BOARD_TTY:       TTY to use on board\n" +
"    SCI_ID:	      The ID that Serial port using for each board"	
"\n" +
"  options:\n" +
"    -h: Dipslay this help message and exit\n" +
"    -v: Be versbose\n" +
"\n" +
"  e.g:\n" +
"    suspend.py armadillo root 1 /dev/ttySC1\n" +
""
    )

# Checking arguments and run
if len(sys.argv) < 1:
    err("Too few arguments\n")
    usage()
try:
    opts, args = getopt.getopt(sys.argv[1:], "hv", [])
except getopt.GetoptError:
    err("Unknown arguments\n")
    usage()

if len(sys.argv) < 5:
    err("Too few arguments\n")
    usage()

for opt, arg in opts:
    if opt == '-h':
        usage();
    if opt == '-v':
        verbose = True

test = Test(*args)
retval = test.run()
if retval == False:
    exit(1)


