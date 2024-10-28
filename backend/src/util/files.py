from pathlib import Path
from util.logUtil import initLog

log = initLog(__file__)

def findFilesRecursive(baseFolder, fileName):
    log.info(f'looking for {fileName} recursively in {baseFolder}')
    return list(Path(baseFolder).rglob(fileName))
