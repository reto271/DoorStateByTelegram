#!/usr/bin/env python3
# encoding: utf-8

import unittest
import os
from UserListHandler import UserListHandler

class Test_UserListHandler(unittest.TestCase):
    def __initializeTest(self):
        if os.path.exists('./testIds.txt'):
            os.remove('./testIds.txt')
        with open('./testIds.txt', 'w') as f:
            f.write('')

    def test_isListEmpty(self):
        self.__initializeTest()
        m_userList = UserListHandler(True)
        m_userList.initialize('./testIds.txt')
        m_userList.loadList()
        self.assertEqual(True, m_userList.isListEmpty())

    def test_addUser(self):
        self.__initializeTest()
        m_userList = UserListHandler(True)
        m_userList.initialize('./testIds.txt')
        m_userList.loadList()
        m_userList.addUser(1234)
        self.assertEqual(False, m_userList.isListEmpty())
        self.assertEqual(True, m_userList.isUserRegistered(1234))
        self.assertEqual(False, m_userList.isUserRegistered(1235))

    def test_removeUser(self):
        self.__initializeTest()
        m_userList = UserListHandler(True)
        m_userList.initialize('./testIds.txt')
        m_userList.loadList()
        m_userList.addUser(1234)
        self.assertEqual(False, m_userList.isListEmpty())
        self.assertEqual(True, m_userList.isUserRegistered(1234))
        self.assertEqual(False, m_userList.isUserRegistered(1235))
        m_userList.removeUser(1234)
        self.assertEqual(True, m_userList.isListEmpty())
        self.assertEqual(False, m_userList.isUserRegistered(1234))
        self.assertEqual(False, m_userList.isUserRegistered(1235))

    def test_getUserList(self):
        self.__initializeTest()
        m_userList = UserListHandler(True)
        m_userList.initialize('./testIds.txt')
        m_userList.loadList()
        m_userList.addUser(12)
        m_userList.addUser(123)
        m_userList.addUser(1234)
        userList = m_userList.getUserList()
        self.assertEqual(3, len(userList))
        self.assertEqual([12, 123, 1234], userList)

    def test_storeLoadList(self):
        self.__initializeTest()
        m_writeList = UserListHandler(True)
        m_writeList.initialize('./testIds.txt')
        m_writeList.loadList()
        m_writeList.addUser(12)
        m_writeList.addUser(123)
        m_writeList.addUser(1234)
        m_writeList.storeList()
        # Assure the list is still correct
        m_readList = UserListHandler(True)
        m_readList.initialize('./testIds.txt')
        m_readList.loadList()
        userList = m_readList.getUserList()
        self.assertEqual(3, len(userList))
        self.assertEqual([12, 123, 1234], userList)

if __name__ == '__main__':
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))
    #unittest.main()  # Calling from the command line invokes all tests
