from threading import Timer, current_thread
import json
import os
from pathlib import Path
import re
import shutil
from typing import Dict
from pathvalidate import sanitize_filepath
import zipfile
import urllib
from service.langchain.langchainUtil import getFilePath
from util.files import createFolder
from util.logUtil import initLog

log = initLog(__file__)


def exportHistory(user: str, history: str) -> Path:
    log.info(f'loading history={getFilePath(user, history)}')
    outDir = sanitize_filepath(getFilePath(user, history, ''))+'/'
    userHistoryDir = sanitize_filepath(getFilePath(user, history, ''))
    createFolder(outDir)
    zipFile = userHistoryDir+'.zip'
    userHistoryDir = userHistoryDir+'/'
    with open(getFilePath(user, history)) as history:
        historyItems: Dict = json.load(history)
        if historyItems:
            readme = outDir+'README.md'
            with zipfile.ZipFile(zipFile, 'w', zipfile.ZIP_DEFLATED) as zip:
                log.info(f'generating history export at {readme}')
                with open(readme, 'w') as readmeWriter:
                    answerDir = ''
                    for item in historyItems:
                        log.info(f'history key {item}')
                        content: str = item['data']['content']
                        type: str = item['data']['type']
                        answerDir = _answerDir(type, answerDir, content)
                        log.info(f'history CONTENT {content}')
                        readmeWriter.write(_moveCodeBlocksToFiles(
                            zip, userHistoryDir, answerDir, content, type))
                zip.write(outDir+'README.md', userHistoryDir+'README.md')
    log.info(f"returning {zipFile}")
    cleanFuture(outDir, zipFile)
    return Path(zipFile).absolute()


def _answerDir(type: str, answerDir, content) -> str:
    if type == 'human':
        answerDir = sanitize_filepath(
            content.split('\n')[0].split('.')[0]) + '/'
    return answerDir


FLAGS = re.IGNORECASE | re.MULTILINE
PATTERN_FILE_FILENAME_CODE = re.compile(
    r'[*]+File: +([a-z_-]+[.][a-z]{1,3})[*]+\n+[`]{3}[a-z-_]+\n+([^`]+)[`]{3}', FLAGS)
PATTERN_FILENAME_CODE = re.compile(
    r'[*]+([a-z_-]+[.][a-z]{1,3})[*]+: *\n+[`]{3}[a-z-_]+\n+([^`]+)[`]{3}', FLAGS)
MIN_LINES = 5


def _moveCodeBlocksToFiles(zip: zipfile.ZipFile, userHistoryDir: str, answerDir: str, content: str, type: str) -> str:
    content = _byPattern(PATTERN_FILE_FILENAME_CODE, zip, userHistoryDir,
                         answerDir, content, type)
    content = _byPattern(PATTERN_FILENAME_CODE, zip, userHistoryDir,
                         answerDir, content, type)
    return content


def _byPattern(pattern: re.Pattern, zip: zipfile.ZipFile, userHistoryDir: str, answerDir: str, content: str, type: str) -> str:
    for fileNamesAndContents in re.finditer(pattern, content):
        log.info(f'fileNamesAndContents {fileNamesAndContents}')
        fileName = fileNamesAndContents.groups()[0]
        fileContent = fileNamesAndContents.groups()[1]
        if len(fileContent.split('\n')) >= MIN_LINES:
            log.info(f'content match to file {fileName}')
            createFolder(userHistoryDir+'/'+answerDir)
            newFilePath = userHistoryDir+'/'+answerDir+fileName
            with open(newFilePath, 'w') as f:
                log.info(f'history file {newFilePath}')
                f.write(f"{fileContent}")
            zip.write(newFilePath, userHistoryDir+'/'+answerDir + fileName)
            mdDirFile = urllib.parse.quote(
                answerDir + fileName, safe='/', encoding=None, errors=None)
            content = re.sub(
                pattern, f'[{fileName}]({mdDirFile})', content, 1)
    prefix = '' if content.startswith('\n##') else (
        '\n## ' if type == 'human' else '\n### Response:\n\n')
    return prefix + content


def cleanFuture(outDir: str, zipFile: str, interval=10):
    def clean(outDir: str, zipFile: str):
        log.info(f'cleaning export folder {outDir} in thread {current_thread}')
        shutil.rmtree('./'+outDir)
        os.remove(zipFile)
    log.info(f'cleaning export in 10secs folder {outDir} in thread {current_thread}')
    Timer(interval=interval, function=clean, args=(outDir, zipFile)).start()
