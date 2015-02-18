#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author    : Thomas Cuthbert
import sys
import paramiko, time
import re

__all__ = ['ssh_cmd']


def ssh_timeout_wait(ssh, timeout):
    "Blocking timeout function"

    while True:
        if ssh.recv_ready():
            break
        if timeout == 0:
            raise
        time.sleep(1)
        timeout -= 1
    return timeout


def ssh_recv(ssh, cmd, expect, buffsize=1024):
    "This function handles recv on ssh channel in an expect sort of way"

    output = list()
    # Keep polling buffer for data.
    # Once all data has been pulled from server, process data
    data = ""
    timeout = 10
    while ssh_timeout_wait(ssh, timeout) > 0:
        timeout = 10
        data += ssh.recv(buffsize)
        if re.search(r"%s" % expect, data):
            break
    # Process data
    push_data = False
    for line in data.splitlines():
        if re.search(expect, line):
            # Now at prompt, return output
            return output
        if re.search(cmd, line):
            # At point in buffer where data is ready to be pushed
            # Skip line in buffer where our command was entered
            push_data = True
            continue
        if push_data:
            output.append(line)


def exec_cmd(ssh, cmd, expect="#", *password):
    "This function execs a given command against ssh connection"

    ssh.send(cmd + "\n")
    return ssh_recv(ssh, cmd, expect)


def escalate(ssh, password, expect):
    from re import search

    exec_cmd(ssh, "enable", expect)
    exec_cmd(ssh, password, expect="#")
    return


def ssh_cmd(username, password, hostname, cmd):
    "The main function"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(
        paramiko.AutoAddPolicy())

    # connect to shell
    ssh.connect(hostname, username=username, password=password, allow_agent=False, look_for_keys=False)
    session = ssh.invoke_shell()
    exec_cmd(session,
             "terminal length 0",
             expect=">",
    )
    escalate(session, password, "password:")
    data = exec_cmd(session,
                    cmd,
                    expect="#$",
    )
    session.close()
    return data
