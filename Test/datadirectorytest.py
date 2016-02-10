import sys
sys.path.append("../")

import unittest

import Algorithmia
from Algorithmia import client
from Algorithmia.datadirectory import DataDirectory
import os

class DataDirectoryTest(unittest.TestCase):
    def setUp(self):
        self.client = client(os.environ['ALGORITHMIA_API_KEY'])

    def test_directory_does_not_exit(self):
        dd = DataDirectory(self.client, "data://.my/this_should_never_be_created")
        self.assertFalse(dd.exists())

    def test_empty_directory_creation_and_deletion(self):
        dd = DataDirectory(self.client, "data://.my/test_directory_creation")

        if (dd.exists()):
            dd.delete()

        self.assertFalse(dd.exists())

        dd.create()
        self.assertTrue(dd.exists())

        # get rid of it
        dd.delete()
        self.assertFalse(dd.exists())

if __name__ == '__main__':
    unittest.main()
