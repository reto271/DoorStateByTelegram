#!/usr/bin/env python3
# encoding: utf-8

import unittest
import os
from UserListHandler import UserListHandler

class Test_UserListHandler(unittest.TestCase):
    def __initializeTest(self):
        if os.path.exists('./testIds.txt'):
            os.remove('./testIds.txt')

    def test_isListEmpty(self):
        self.__initializeTest()
        m_userList = UserListHandler(False)
        m_userList.initialize('./testIds.txt')
        m_userList.loadList()
        self.assertEqual(False, m_userList.isListEmpty())


#unittest.main()  # Calling from the command line invokes all tests
if __name__ == '__main__':
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))
