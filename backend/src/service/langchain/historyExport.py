from datetime import datetime
import logging
from threading import Timer
import json
import os
from pathlib import Path
import re
import shutil
from typing import Dict
from pathvalidate import sanitize_filepath
import zipfile
import urllib
from unidecode import unidecode
from service.langchain.langchainUtil import getFilePath, getSessionHistoryName
from service.langchain.prompByModel import ANSWER_TITLE_FROM_QUESTION, cleanMarkdown, getFilenameCodePattern, getSpecifications
from util.files import createFolder
from util.logUtil import initLog

FILE_CONTENT_MIN_LINES = 1
log = initLog(__file__, logging.DEBUG)


# autopep8: off
def exportHistory(user: str, history: str) -> Path:
    session = getSessionHistoryName(user, history)
    log.info(f'exportHistory loading history={getFilePath(session)}')
    outDir = sanitize_filepath(getFilePath(session, ''))+'/'
    userHistoryDir = sanitize_filepath(getFilePath(session, ''))
    createFolder(outDir)
    zipFile = userHistoryDir+'.zip'
    userHistoryDir = userHistoryDir+'/'
    with open(getFilePath(session)) as history:
        historyItems: Dict = json.load(history)
        if historyItems:
            readme = outDir+'README.md'
            with zipfile.ZipFile(zipFile, 'w', zipfile.ZIP_DEFLATED) as zip:
                log.debug(f'generating history export at {readme}')
                processHistoryItems(session, zip, historyItems, userHistoryDir, readme)
                zip.write(outDir+'README.md', userHistoryDir+'README.md')
    log.debug(f"returning {zipFile}")
    _cleanFuture(outDir, zipFile)
    return Path(zipFile).absolute()


def processHistoryItems(session, zip, historyItems, userHistoryDir, readme):
    with open(readme, 'w') as readmeWriter:
        readmeWriter.write(f'# openai-local-ollama-chat history {getFilePath(session)}\n\nExport date: {datetime.now().strftime("%Y-%b-%d %X")}')
        question = ''
        for item in historyItems:
            content: str = item['data']['content']
            type: str = item['data']['type']
            log.info(f'processHistoryItems data = {json.dumps(item)}')
            if type == 'human':
                question = content
            else:
                model = item['data']['response_metadata']['model_name']
                specs = getSpecifications(model)
                log.debug(f'history CONTENT {content}')
                if specs.get(ANSWER_TITLE_FROM_QUESTION, False):
                    content = question + '\n\n' + content
                answerDir = _answerDir(specs, content)
                newContent = _moveCodeBlocksToFiles(specs, zip, userHistoryDir, answerDir, content)
                newContent = cleanMarkdown(model, newContent)
                readmeWriter.write(newContent)
        readmeWriter.write('\n')


def _answerDir(specs: Dict, content) -> str:
    dir: str = content.split('\n')[0].split('.')[0]
    log.info(f'answerDir specs {specs} ')
    # if specs.get(ANSWER_DIR_REGEX, ''):
    #     regex: list = specs[ANSWER_DIR_REGEX]
    #     log.info(f'answerDir applying {ANSWER_DIR_REGEX} found -> {regex}')
    #     log.info(f'answerDir current dir is {dir}')
    #     dir = re.sub(re.compile(regex), r'\1', dir)
    #     log.info(f'answerDir dir is {dir}')
    return sanitize_filepath(dir[0].upper()+dir[1:]) + '/'


def _moveCodeBlocksToFiles(specs: Dict, zip: zipfile.ZipFile, userHistoryDir: str, answerDir: str, content: str) -> str:
    pattern = getFilenameCodePattern(specs)
    for fileNamesAndContents in re.finditer(pattern, content):
        fileNameOriginal = fileNamesAndContents.group('fileName')
        fileName = unidecode(fileNameOriginal)
        fileContent = fileNamesAndContents.group('content')
        log.debug(f'fileNames: {fileName} content: {fileContent}')
        if fileName and fileContent and len(fileContent.split('\n')) >= FILE_CONTENT_MIN_LINES:
            log.debug(f'content match to file {fileName}')
            newFilePath = sanitize_filepath(userHistoryDir+'/'+answerDir+fileName)
            createFolder(os.path.dirname(newFilePath))
            with open(newFilePath, 'w') as f:
                log.debug(f'history file {newFilePath}')
                f.write(f"{fileContent}")
            zip.write(newFilePath, userHistoryDir+'/'+answerDir + fileName)
            mdDirFile = urllib.parse.quote(answerDir + fileName, safe='/', encoding=None, errors=None)
            content = re.sub(pattern, f'[{fileName}]({mdDirFile})\n', content, 1)
    prefix = '\n\n' if content.startswith('##') else '\n\n## '
    return prefix + content


def _clean(outDir: str, zipFile: str):
    # log.debug(f'cleaning export folder {outDir} in another thread')
    shutil.rmtree('./'+outDir)
    os.remove(zipFile)

def _cleanFuture(outDir: str, zipFile: str, interval=10):
    log.debug(f'cleaning export in {interval}secs folder {outDir} in thread ')
    Timer(interval=interval, function=_clean, args=(outDir, zipFile)).start()
