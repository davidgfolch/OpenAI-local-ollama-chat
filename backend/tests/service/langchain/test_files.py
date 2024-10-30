from pathlib import Path
from typing import Generator

import pytest

from constants import UPLOAD_FOLDER
from service.langchain.files import ERR_DUPLICATED_FILE, loadFile, processFiles
from service.serviceException import ServiceException
from langchain_community.document_loaders import TextLoader
from unittest.mock import patch
from contextlib import contextmanager

FILE = 'file.txt'
FILE2 = 'file2.txt'
FILE_CONTENT = 'Test file content'


@contextmanager
def mockManager(rglob, loader) -> Generator:
    with patch.object(Path, 'rglob') as m_rglob, patch.object(TextLoader, 'load') as m_loader:
        m_rglob.return_value = rglob
        m_loader.return_value = loader
        yield


@pytest.mark.parametrize("mockManagerParams", [({'rglob': [FILE], 'loader': [[FILE_CONTENT]]}),
                                               ({'rglob': [UPLOAD_FOLDER+FILE], 'loader': [[FILE_CONTENT]]})])
def test_loadFile(mockManagerParams):
    with mockManager(**mockManagerParams):
        res = loadFile(mockManagerParams['rglob'][0])
        assert res == mockManagerParams['loader'][0]


def test_loadFile_notFound():
    with pytest.raises(ServiceException) as ex:
        loadFile('non_existent_file.txt')
    assert str(ex.value) == "non_existent_file.txt not found, upload it first!"


def test_loadFile_multipleFound():
    with mockManager([FILE, FILE], [FILE_CONTENT, FILE_CONTENT]):
        with pytest.raises(ServiceException) as ex:
            loadFile(FILE)
        assert str(ex.value) == ERR_DUPLICATED_FILE.format(FILE)


def test_processFiles():
    with mockManager([FILE], [FILE_CONTENT]):
        res = processFiles([FILE])
        assert res == [FILE_CONTENT]
        res = processFiles([FILE, FILE])
        assert res == [FILE_CONTENT]
