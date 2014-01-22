#!/usr/bin/python

# wakeup.py
# After run suspend.py please run this program.

import errno
import getopt
import os
import select
import subprocess
import sys
import time

def try_kill (proc):
    try:
        proc.kill()
    except OSError, e:
        if e.errno != errno.ESRCH:
            print >>sys.stderr, 'error: kill failed:', e
            return False

    return True

verbose = False

def info (str):
    if verbose:
        print str
    pass

def err_stdio(msg, outdata, errdata):
    msg += '\nStdout:'
    if outdata:
        msg += '\n' + outdata.rstrip('\r\n') + '\n'
    msg += '\nStderr:'
    if errdata:
        msg += '\n' + errdata.rstrip('\r\n') + '\n'
    err(msg.rstrip('\r\n'))

class Test:
    def __init__(self, local_tty, board_hostname, board_username, board_tty, sci_id):
        self.local_tty = local_tty
        self.board_hostname = board_hostname
        self.board_username = board_username
	self.board_tty = board_tty
	self.sci_id = sci_id

#Call subprocess to send command
    def call_cmd(self, cmd):
	board_arg = ['ssh',self.board_username + '@' + self.board_hostname ] + cmd
	run_cmd = subprocess.call(board_arg)
	return run_cmd

    def start_cmd(self, info_str, cmd, stdin=None):
        info(info_str)
        info('start_cmd: ' + ' '.join(cmd))

        pipes = {'stdout':subprocess.PIPE, 'stderr':subprocess.PIPE}
        if stdin:
            pipes['stdin'] = stdin

        try:
            proc = subprocess.Popen(cmd, **pipes)
        except OSError as e:
            print >>sys.stderr, 'error: ' + info_str + ': execution failed:', e
            return None

        return proc

    def echo_args(self, tty):
        return [ 'dd', 'bs=1', 'of=' + tty ]

    def echo(self, info_str, key):
        retcode = True

        cmd = self.echo_args(self.local_tty)

        proc = self.start_cmd(info_str, cmd, stdin=subprocess.PIPE)
        if not proc:
            return False

        (outdata, errdata) =  proc.communicate('\n' * 1 + key + '\n');
        if proc.returncode != 0:
           err_stdio(info_str, outdata, errdata)
           retcode = False

        if not try_kill(proc):
            retcode = False

        return retcode

#Preparing a command before called
    def prepare_cmd(self, msg):
	cmd = [ '/bin/echo', msg, '>', '/dev/null' ]
	return [ ' '.join(cmd) ]

    def run_check(self, msg):

	param_str = self.prepare_cmd(msg)
	cal_cmd = self.call_cmd(param_str)
	
	return cal_cmd

# Running:
    def run(self):
        ok = 0
        ng = 0
        status = True
	check = 'probe'
	print "Check the suspending system..."
	probe1 = self.run_check(check)
	if (probe1 == 0):
		print "System hasn't been suspended!"
		ng = ng + 1
	else:
		print "Because the system is suspending!\n"
		info_str = 'send a data to wakup device'
		key = ' '
		# Send a data to board via serialport to wakeup system.
		data = self.echo(info_str, key)
		if not data:
			print "Send a data failed!"
			ng = ng + 1
		else:
			print "Check the wakeup device..."
			time.sleep(2)
			check = 'wakeup'
			probe2 = self.run_check(check)
			if (probe2 == 0):
				print "System has been waked up!"
				ok = ok + 1
			else:
				print "wakeup the system failed!!" 
				ng = ng + 1

        print "Test Complete: Passed=%d Failed=%d" % (ok, ng)
        if ng != 0:
        	status = False
	
        return status

# Help
def usage():
        fatal_err(
"Usage: suspend.py [options] LOCAL_TTY \\\\n" +
"                      BOARD_HOSTNAME BOARD_USERNAME BOARD_TTY SCI_ID\\\\n" +
"  where:\n" +
"\n"
"    LOCAL_TTY:       TTY to use on local host\n"
"    BOARD_HOSTNAME:  Is the hostname of the board to connect to\n" +
"    BOARD_USERNAME:  Is the username to use when when loging into the board\n" +
"    BOARD_TTY:       TTY to use on board\n"+
"    SCI_ID:	      The ID that Serial port using for each board"	
"\n" +
"  options:\n" +
"    -h: Dipslay this help message and exit\n" +
"    -v: Be versbose\n" +
"\n" +
"  e.g:\n" +
"    wakeup.py /dev/ttyUSB0 armadillo root /dev/ttySC1 1 \n" +
""
    )

#----------------------------
# Checking arguments and run
if len(sys.argv) < 1:
    err("Too few arguments\n")
    usage()
try:
    opts, args = getopt.getopt(sys.argv[1:], "hv", [])
except getopt.GetoptError:
    err("Unknown arguments\n")
    usage()

if len(sys.argv) < 6:
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

#===================================

