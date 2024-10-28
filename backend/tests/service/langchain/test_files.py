import copy
from pathlib import Path
from typing import Generator
import unittest
from tests.common import USER_DATA
from service.langchain.files import loadFile, processFiles
from service.serviceException import ServiceException
from langchain_community.document_loaders import TextLoader
from unittest.mock import patch
from contextlib import contextmanager

FILE = 'file.txt'
FILE_CONTENT = 'Test file content'


@contextmanager
def mockManager(rglob, loader) -> Generator:
    with patch.object(Path, 'rglob') as m_rglob, patch.object(TextLoader, 'load') as m_loader:
        m_rglob.return_value = rglob
        m_loader.return_value = loader
        yield


class TestFiles(unittest.TestCase):

    def test_loadFile(self):
        with mockManager([FILE], [FILE_CONTENT]):
            result = loadFile(FILE)
            self.assertEqual(result, FILE_CONTENT)

    def test_loadFile_notFound(self):
        with self.assertRaises(ServiceException) as ex:
            loadFile('non_existent_file.txt')
        self.assertEqual(str(ex.exception),
                         "non_existent_file.txt not found, upload it first!")

    def test_loadFile_multipleFound(self):
        with mockManager([FILE, FILE], [FILE_CONTENT, FILE_CONTENT]):
            with self.assertRaises(ServiceException) as ex:
                loadFile(FILE)
            self.assertEqual(
                str(ex.exception), "Found several file.txt files in upload folder & sub-folders.")

    def test_processFiles(self):
        userData = copy.deepcopy(USER_DATA)
        userData.question = '@file.ext @file.ext'
        with mockManager([FILE], [FILE_CONTENT]):
            res = processFiles(userData)
            self.assertEqual(res, [userData.question, [FILE_CONTENT]])


if __name__ == '__main__':
    unittest.main()
