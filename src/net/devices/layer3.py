#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author    : Thomas Cuthbert
import os, sys
from device import Device
from config.config import Config


class Layer3(Device):
    def __init__(self, *args, **kwargs):
        "Initialise device object with initial values."
        super(Layer3, self).__init__(*args, **kwargs)
