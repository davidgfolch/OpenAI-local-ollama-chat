import re
from typing import Any, List
from langchain_community.document_loaders import TextLoader

from constants import UPLOAD_FOLDER
from service.langchain.model import UserData
from service.serviceException import ServiceException
from util.files import findFilesRecursive
from util.logUtil import initLog


log = initLog(__file__)


def loadFile(fileName):
    found = False
    log.info(f"Looking for file {fileName}")
    files = findFilesRecursive(UPLOAD_FOLDER, fileName)
    for path in files:
        if found:
            raise ServiceException(
                f'Found several {fileName} files in upload folder & sub-folders.')
        found = True
        log.info(f"Loading file path={path}")
        loader = TextLoader(path)
        res = loader.load()[0]
    if not found:
        raise ServiceException(f'{fileName} not found, upload it first!')
    return res


def processFiles(d: UserData) -> str | List[Any]:
    files = []
    fileNames = {}
    for matchObj in re.finditer('@([a-zA-Z_\\-.0-9]+(\\.[a-zA-Z]{1,3})?)', d.question):
        fileName = matchObj.group(1)
        log.info(f"fileNames = {fileNames}")
        if fileNames.get(fileName, False):
            log.info(f"Ignoring loading duplicated file={fileName}")
        else:
            files.append(loadFile(fileName))
            fileNames.update({fileName: True})
    d.question = re.sub(
        r'@([a-zA-Z_\-.0-9]+(\.[a-zA-Z]{1,3})?)', r'\1', d.question)
    return d.question if files.count == 0 else [d.question, files]
