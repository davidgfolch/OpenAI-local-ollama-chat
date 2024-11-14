from re import Pattern
from enum import Enum
import re
from typing import Dict
from util.logUtil import initLog


log = initLog(__file__)


class Model(Enum):
    LLAMA_3_2 = 'llama3.2'
    QWEN_2_5_CODER = 'qwen2.5-coder'


# autopep8: off
FLAGS = re.IGNORECASE | re.MULTILINE | re.DOTALL
# PATTERN_FILE_NAME = '([a-z_-]+[.][a-z]{1,3})'
# PATTERN_CODE_BLOCK = '[`]{3}[a-z_-]+ *\n+ *((?!```).*\n)+[`]{3}'
VALID_FOLDER_FILE_CHARS = '[a-zá-úà-ùä-üâ-ûñç_]+[a-zá-úà-ùä-üâ-ûñç0-9_-]*'
PATH_REGEX = '(?P<fileName>(' + VALID_FOLDER_FILE_CHARS + '/)*' + VALID_FOLDER_FILE_CHARS + '([.][a-z]{1,4})+)'
CODE_BLOCK = '^```[a-z-_]*\\s*\n(?P<content>.*?)(?=^```)```'
# NOTE: ABILITY_FORMAT, if you change the format historyExport.py is affected (regular expressions)
ABILITY_FORMAT = 'abilityFormat'
ANSWER_DIR_REGEX = 'answerDirRegex'
ANSWER_TITLE_FROM_QUESTION = 'answerFolderFromQuestion'
FILENAME_CODE_PATTERN = 'filenameCodePattern'
MODEL_SPECS = {
    Model.LLAMA_3_2.value: {
        ABILITY_FORMAT: """

            IMPORTANTE:
            - Antes de cada bloque de código generar un nombre de archivo con su extension.
            - No repetir bloques de código, usar parametrización.

            En el caso de generar bloques de de código las respuesta debe incluir un script de instalación para las librerias necesarias (sin comentarios añadidos, y sin nombre de archivo).
                - los bloques de código generados deben seguir las siguientes directrices:
                    - incluir siempre el tipo de codigo generado sólo en la cabecera de codigo markdown.
                    - evitar los comentarios evidentes, pero generando comentarios explicativos.
                    - evitar saltos de linea innecesarios.""",
        FILENAME_CODE_PATTERN: '[*`]+' + PATH_REGEX + '[`:*]+[^\n]*\n+' + CODE_BLOCK
    },
    Model.QWEN_2_5_CODER.value: {
        ABILITY_FORMAT: """

            La respuesta tiene que tener la siguiente estructura:
            - Genera un título conciso y corto
            - En la siguiente linea genera una pequeña explicacion.
            - Antes de cada bloque de código genera el nombre del archivo incluyendo su path relativo.

""",
        ANSWER_TITLE_FROM_QUESTION: True,  # LLM ignores prompt asking for title in response
        # ANSWER_DIR_REGEX: '.*Claro.+ejemplo completo de (.+)', # TODO: to use that remove comment in historyExport.py
        FILENAME_CODE_PATTERN: '### Nombre del Archivo: [*`]+' + PATH_REGEX + '[`:*]+[^\n]*\n+' + CODE_BLOCK
    }
}
# autopep8: on


def getSpecifications(model: str) -> str:
    modelUsed = model
    specs = MODEL_SPECS.get(modelUsed)
    if not specs:
        modelUsed = model.split(':')[0]
        specs = MODEL_SPECS.get(modelUsed)
        if not specs:  # get first (default)
            firstKey = next(iter(MODEL_SPECS))
            modelUsed = firstKey
            specs = MODEL_SPECS.get(firstKey)
    log.info(f'specification model {modelUsed}')
    if specs:
        log.info(f'Using abilityFormat {modelUsed} for model {model}')
    return specs if specs else ''


def getFilenameCodePattern(specs: Dict) -> Pattern:
    return re.compile(specs[FILENAME_CODE_PATTERN], FLAGS)

# autopep8: off
def cleanMarkdown(model: str, md: str) -> str:
    """remove markdown lint warnings by model"""
    if model.startswith(Model.LLAMA_3_2.value):
        md = re.sub(r'[*]+Código de ejemplo:?[*]+', '', md, FLAGS)  # remove repetitive "header"
        md = re.sub(r'[*]+Instalación de las librerías:?[*]+', '', md, FLAGS)  # remove repetitive "header"
        md = re.sub(r'\n[*]{2}([^*]+)[*]{2}\s?\n', r'\n### \1\n\n', md, FLAGS)  # replaces **(.*)** by ### .*
        md = re.sub(r'\n[*]   ', '\n* ', md, FLAGS)  # replaces list spaces (*   xxx by * xxx)
        md = re.sub(r'(\n+[#]+ +)[*]{2}([^*]+)[*]{2}(\s?\n)', r'\1\2\3', md, FLAGS)  # remove ** from titles
        md = re.sub(r'(?<=\b)([a-z]{3,5}://[a-z][a-z0-9_-]+(:\d{1,5}|\.[a-z]{2,10})(/[a-z][a-z0-9_-]+)*(/)?)(?=\b)', r' <\1> ', md, FLAGS)  # http://localhost:8000/ -> <http://localhost:8000/>
    elif model.startswith(Model.QWEN_2_5_CODER.value):
        for match in re.finditer(r'(?<!```\n) *```[a-z]*\n([^\n]+\n)*(?!=```[a-z])', md, FLAGS):
            if not match.group(1):
                md = md[0:match.start(0)] + md[match.end(0):]
    md = re.sub(r'\n([^-][^ ][^\n]+)\n(- .+\n)', r'\1\n\n\2', md, FLAGS)
    md = re.sub(r'(?<!\d. )(.+)\n(1. .+)', r'\1\n\n\2', md, FLAGS)
    md = re.sub(r'(#+ +[^\n]+)[.:!]+\n', r'\1\n', md, FLAGS)  # removes punctuation on titles .:!
    md = re.sub(r'(?<!\n)\n( *```[a-z]+)', r'\n\n\1', md, FLAGS)  # add blank line BEFORE code block
    md = re.sub(r'(?<!\n)(\n *```)\n(?!=\n)', r'\1\n\n', md, FLAGS)  # add blank line AFTER code block
    md = re.sub(r'[\n]{3,}', r'\n\n', md, FLAGS)  # replaces more than 3 empty lines by only 2
    return md
# autopep8: on
