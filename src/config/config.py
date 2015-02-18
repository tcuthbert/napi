#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author    : Thomas Cuthbert
import os, sys, inspect
import ConfigParser
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Config(object):
    "docstring"

    ini_path = os.path.dirname(
        os.path.abspath(
            inspect.getfile(
                inspect.currentframe()))) + "example.ini"

    @classmethod
    def set_config_path(cls, path="example.ini"):
        Config.ini_path = path
        
    @classmethod
    def __init__(cls, *args, **kwargs):
        cls.__config = ConfigParser.ConfigParser()
        cls.__config.read(cls.ini_path)
        
    @classmethod
    def config_section_map(cls, section):
        section_map = {}
        options = cls.__config.options(section)
        for option in options:
            try:
                section_map[option] = cls.__config.get(section, option)
                if section_map[option] == -1:
                    logger.debug("skip: %s" % option)
            except:
                logger.debug("exception on %s!" % option)
                section_map[option] = None

        return section_map
  
