#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author    : Thomas Cuthbert
import os, sys
from providers.provider import Provider
from config.config import Config
from util.ssh_cmd import ssh_cmd


class SSH(Provider):
    def __init__(self, *args, **kwargs):
        "docstring"
        super(SSH, self).__init__(*args, **kwargs)

    def run_command(self, cmd):
        """Execute cmd against bound device
        :param cmd: string containing ios command
        :type cmd: str
        """
        c = Config.config_section_map("CREDS")
        username = c['username']
        password = c['password']
        return ssh_cmd(username, password, self._device.hostname, cmd)

