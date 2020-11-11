#!/usr/bin/env python3
# encoding: utf-8

import argparse
import os.path
import os
import sys
import subprocess

from datetime import date

# My modules
import myUtils
import ProjectVersion
from UserListHandler import UserListHandler
from ValidateDate import ValidateDate

def main():
    """ The main entry point of the analyse log script
    """
    feedback = -1
    options = parse_options()

    # Load the list of the users, some options require it.
    registeredUserList = loadRegisteredUsers()

    # Process the options
    if options.notRegUser is True:
        feedback = dumpRequestsOfNotRegisteredUsers(options.logFileName[0], registeredUserList)
    elif options.version is True:
        print('Script version: ' + ProjectVersion.getVersionNumber())
        feedback = 0
    elif options.date:
        feedback = dumpLogOfDay(options.logFileName[0], options.date)
    elif options.today is True:
        feedback = dumpLogOfDay(options.logFileName[0], str(date.today()))
    else:
        print('No action specified')

    return feedback


def loadRegisteredUsers():
    userAccessList = UserListHandler(True)
    userAccessList.initialize('./cnfg/registeredIds.txt')
    userAccessList.loadList()
    return userAccessList


def dumpRequestsOfNotRegisteredUsers(logFileName, registeredUserList):
    searchKey = ': Request ['
    try:
        f = open(logFileName,'r')
    except:
        print('File ' + str(logFileName) + ' not found.')
        return -2

    print('--- Requests of non-registered useres:')
    for line in f:
        pos = line.find(searchKey)
        if 0 <= pos:
            foundLine = line.rstrip()
            userId = extractUserId(foundLine[pos+len(searchKey):])
            #print(foundLine + ',    UserId: "' + str(userId) + '"')
            if False == registeredUserList.isUserRegistered(userId):
                print(foundLine)
    f.close()
    print('--- Requests of non-registered useres:')
    return 0

def dumpLogOfDay(logFileName, dateString):
    dateObj = ValidateDate(dateString)
    if True == dateObj.isValid():
        try:
            f = open(logFileName,'r')
        except:
            print('File ' + str(logFileName) + ' not found.')
            return -3

        inDate = False
        for line in f:
            dateLine = ValidateDate(line.rstrip())
            if True == dateLine.isValid():
                if ((dateObj.getDay() == dateLine.getDay()) and
                    (dateObj.getMonth() == dateLine.getMonth()) and
                    (dateObj.getYear() == dateLine.getYear())):
                    inDate = True
                else:
                    inDate = False

            if True == inDate:
                print(line.rstrip())
        return 0
    else:
        print('Date string "' + dateString + '" is not valid.')
        return -4

def extractUserId(userInfo):
    startPos = 1 + userInfo.find(']')
    endPos = userInfo.find(' ', startPos + 1)
    userId = userInfo[startPos:endPos]
    return myUtils.tryInt(userId)

#def run_tests(options, config):
#    ''' Run the tests as specified with the command line if non specified search
#        if unit is available and if available run it.
#    '''
#    if len(options.tests) == 0:
#        options.tests = ['unit']
#
#    for test in get_tests(config, options.tests):
#        err = 0
#        if 'setup' in config['Tests'][test]:
#            print("Setup: {}".format(test))
#            cmd = resolve_vars_in_command(config['Tests'][test]['setup'],
#                                          options)
#            err = run_command(cmd, options.verbose)
#
#        if err == 0:
#            print("Run: {}".format(test))
#            cmd = resolve_vars_in_command(config['Tests'][test]['command'],
#                                          options)
#            if (options.ignoreFailedTests and
#                    'ignore-failed-tests' in config['Tests'][test]):
#                cmd += config['Tests'][test]['ignore-failed-tests']
#            err = run_command(cmd, options.verbose)
#
#        if 'teardown' in config['Tests'][test]:
#            print("TearDown: {}".format(test))
#            cmd = resolve_vars_in_command(config['Tests'][test]['teardown'],
#                                          options)
#            run_command(cmd, options.verbose)
#        if err != 0:
#            return err
#
#    return 0


#def run_command(cmd, verbose):
#    ''' Run the given command '''
#    if verbose:
#        print(" -> {}".format(cmd))
#    # don't use call, child process will not receive any chance to
#    # handle KeyboardInterrupt
#    with subprocess.Popen(cmd) as command:
#        try:
#            command.wait()
#            if command.returncode != 0:
#                print("Error {} on {}".format(command.returncode, cmd))
#            return command.returncode
#        except KeyboardInterrupt:
#            try:
#                command.wait(timeout=30)
#            except subprocess.TimeoutExpired:
#                command.kill()
#                print("Abort timed out")
#            print("Aborted by keyboard interrupt on: {}".format(cmd))
#            exit(66)


#def resolve_vars_in_command(cmd, options):
#    ''' Resolve all variables found in the command. Currently the following
#    variables are supported:
#    PROJECTDIR, BUILDDIR, INSTALLDIR
#    '''
#    result = []
#    for part in cmd:
#        part = part.replace('${PROJECTDIR}', options.projectdir)
#        part = part.replace('${BUILDDIR}', options.builddir)
#        part = part.replace('${INSTALLDIR}', options.installdir)
#        result.append(part)
#    return result


#def get_tests(config, testlist):
#    ''' Get all the tests for list of testnames '''
#    result = []
#    for test in testlist:
#        if test in config['Groups']:
#            for gtest in get_tests(config, config['Groups'][test]['tests']):
#                if gtest not in result:
#                    result.append(gtest)
#        elif test in config['Tests']:
#            if test not in result:
#                result.append(test)
#        else:
#            print("Test not found within test.config: {}".format(test))
#            exit(2)
#    return result


#def print_test_list(config):
#    ''' Print a list with all the tests including their description. '''
#    print("Tests:")
#    for test in config['Tests']:
#        print("- {:<20}{}".format(test,
#                                  config['Tests'][test]['description']))
#
#    print("\nGroups:")
#    for group in config['Groups']:
#        print("- {:<20}{}".format(group,
#                                  config['Groups'][group]['description']))
#
#        for test in config['Groups'][group]['tests']:
#            print("{:<20}  - {}".format("", test))


def read_location_entry(projectdir, entryname):
    '''
    Reads the given entry from the location file.
    :projectdir: path to the project directory
    :entryname: name of the entry in the file
    :return: entry value if found otherwise None
    '''
    location_file = os.path.join(projectdir, ".location")
    if os.path.exists(location_file):
        for line in open(location_file).readlines():
            values = line.split("=")
            if entryname == values[0]:
                return values[1].strip('\n\t')
    return None


def parse_options():
    ''' Parse the command line. '''
    parser = argparse.ArgumentParser(description="Door Bot Log File Analyzer")
    parser.add_argument('logFileName', metavar='LogFile', type=str, nargs=1,                        help='The log file to be analyzed.')
#    parser.add_argument('-n', '--notRegUser', default=None, help='Users not registered, tried to gain access')
    parser.add_argument('-n', '--notRegUser', action='store_true', default=False, help='Users not registered, tried to gain access')
    parser.add_argument('-v', '--version', action='store_true', default=False, help='Users not registered, tried to gain access')
    parser.add_argument('-d', '--date', default=None, help='Print log of the given day, format DATE yyyy-mm-dd')
    parser.add_argument('-t', '--today', action='store_true', default=False, help='Print log of today')

    options = parser.parse_args()

#    if options.notRegUser is None:
#        print('Option -n --notRegUser is not used')
#    else:
#        print('Option -n --notRegUser is used, value is: ' + str(options.notRegUser))

    return options


#def add_python_path(inst_path):
#    ''' Add the inst_path/lib/python3 to the python env variabel to run the
#        tests without setting a path.
#    '''
#    path = os.getenv('PYTHONPATH', None)
#    instpath = os.path.join(inst_path, 'lib', 'python3')
#    if path is None:
#        os.environ['PYTHONPATH'] = instpath
#    else:
#        os.environ['PYTHONPATH'] = ':'.join([path, instpath])

#---------------------------------------------------------------------------
if __name__ == '__main__':
    exit(main())
