#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author    : Thomas Cuthbert
import os, sys
sys.path.append('../src/')
import unittest
from config import Config


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.test_config = Config('../src/example.ini')
        
    def test_init(self):
        from ConfigParser import ConfigParser
        self.assertIsInstance(self.test_config, Config)
        self.assertIsInstance(self.test_config._Config__filep, str)

    def test_config_section_map(self):
        test_section_oids = self.test_config.config_section_map('OIDS')
        self.assertIsNotNone(test_section_oids)
        self.assertGreater(len(test_section_oids), 0)
        


def main():
    unittest.main()


if __name__ == '__main__':
    main()
