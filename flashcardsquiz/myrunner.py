'''
Created on Sep 24, 2017

@author: louie
'''

from subprocess import Popen, PIPE


class MyRunner():
    '''
    Methods to run a process, where I/O can be redirected to variables and files.
    '''

    def __init__(self):
        '''
        Constructor
        '''

    def run_with_input_from_file(self, command='/home/louie/anaconda3/bin/python', args='', input_file='input.dat'):
        '''
        Run a command with optional arguments, using input from a file, returning output.

        args is a string with each arg separated by a space.
        args can be ''           # no args
                    '-lart'      # one arg
                    '/bin -lart' # multiple args
        '''

        myinput = open(input_file)

        command_with_args = [command]

        # if arguments are not given, the command+arg list is just [command]
        # otherwise we'll create an list of args and add the contents of that
        # list to the command+arg list giving [command arg1 arg2 arg3]
        if (args != ''):
            command_with_args += args.split()

        p = Popen(command_with_args,
                  stdin=myinput, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate(
            b"input data that is passed to subprocess' stdin")

        myinput.close()

        rc = p.returncode
        if(rc):
            print("oops!, rc=", rc)

        if(err):
            print("oops!, err=")
            print(err.decode('utf-8'))

        return output.decode('utf-8')
