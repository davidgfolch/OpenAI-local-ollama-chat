from typing import List, Set
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader

from constants import UPLOAD_FOLDER
from service.serviceException import ServiceException
from util.files import findFilesRecursive
from util.logUtil import initLog


log = initLog(__file__)

ERR_DUPLICATED_FILE = 'Found several {} files in upload folder & sub-folders.'


def loadFile(fileName: str) -> Document:
    found = False
    log.info(f"Looking for file {fileName}")
    if fileName.startswith(UPLOAD_FOLDER):
        loader = TextLoader(f'./{fileName}')
        found = True
    else:
        files = findFilesRecursive(UPLOAD_FOLDER, fileName)
        for path in files:
            if found:
                raise ServiceException(ERR_DUPLICATED_FILE.format(fileName))
            found = True
            log.info(f"Loading file path={path}")
            loader = TextLoader(path)
    if not found:
        raise ServiceException(f'{fileName} not found, upload it first!')
    return loader.load()[0]


def processFiles(files: Set[str]) -> List[Document]:
    found = []
    namesFound = {}
    log.info(f"processFiles -> files ={files}")
    for fileName in files:
        if namesFound.get(fileName, False):
            log.info(f"Ignoring loading duplicated file={fileName}")
        else:
            found.append(loadFile(fileName))
            namesFound.update({fileName: True})
            log.info(f"found = {found}")
    return found
