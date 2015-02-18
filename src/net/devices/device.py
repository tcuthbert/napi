#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author    : Thomas Cuthbert
import os, sys
sys.path.append('../../')
from providers.provider import Provider
from config.config import Config


class Device(object):
    @staticmethod
    def _get_site_code_from_hostname(hostname):
        return hostname[1:5]
        
    def __init__(self, device, prov, *args, **kwargs):
        "TODO"
        self._hostname = str(device[""]).lower()
        self.site_code = Device._get_site_code_from_hostname(self._hostname)
        if "" in self.site_code or "" in self.site_code:
            self.device_type = "core"
        else:
            self.device_type = "remote"
        self.provider = prov

        
    def __add__(self, s):
        return str(self.hostname) + str(s)

    def __repr__(self):
        return self.hostname

    @property
    def hostname(self):
        return self._hostname

    @property
    def provider(self):
        return self._provider

    @provider.setter
    def provider(self, value, *args, **kwargs):
        try:
            issubclass(value, Provider)
        except Exception as e:
            #TODO: LOGGING
            raise

        self._provider = value(self)

    @provider.deleter
    def provider(self):
        del self._provider
