#!/usr/bin/env python3
# encoding: utf-8

import os
import unittest
import xmlrunner
import shutil


if __name__ == '__main__':
    root_dir = os.path.dirname(__file__)
    shutil.rmtree(root_dir + '/test-reports')
    test_loader = unittest.TestLoader()
    package_tests = test_loader.discover('.', pattern='Test_*.py')

    testRunner = xmlrunner.XMLTestRunner(output='test-reports')
    testRunner.run(package_tests)
