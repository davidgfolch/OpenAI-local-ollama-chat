import os
from pathlib import Path
from typing import List
from util.logUtil import initLog

log = initLog(__file__)


def findFilesRecursive(baseFolder: str, fileName: str) -> List[Path]:
    log.info(f'looking for {fileName} recursively in {baseFolder}')
    return list(Path(baseFolder).rglob(fileName))


def createFolder(folder: str) -> None:
    if not os.path.exists(folder):
        os.makedirs(folder)
