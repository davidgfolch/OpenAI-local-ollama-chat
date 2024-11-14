from threading import Timer
import unittest
from unittest.mock import patch, mock_open, MagicMock
import zipfile
import json

from service.langchain.historyExport import FILE_CONTENT_MIN_LINES, exportHistory, _answerDir, _moveCodeBlocksToFiles, _cleanFuture
from service.langchain.prompByModel import Model, getSpecifications
# from service.langchain.prompByModel import FILENAME_CODE_PATTERN

# Constants for test
USER = 'test_user'
HISTORY = json.dumps([
    {
        'data': {
            'content': 'question',
            'type': 'human',
            'response_metadata': {}
        }
    },
    {
        'data': {
            'content': 'response',
            'type': 'AIMessageChunk',
            'response_metadata': {
                'model_name': Model.LLAMA_3_2.value
            }
        }
    },
    {
        'data': {
            'content': 'response',
            'type': 'AIMessageChunk',
            'response_metadata': {
                'model_name': Model.QWEN_2_5_CODER.value
            }
        }
    }
])
TEST_EXPORT_OUTPUT_DIR = 'test_export_output'
ANSWER_DIR = 'answer_dir'
ZIP_FILE_PATH = 'test_history.zip'
CONTENT_FILE = 'test_file.py'
CONTENT = """## Sample Content for Testing"""
SUT_PREFIX = 'service.langchain.historyExport'
FILE_CONTENT = 'print(\'Hello\')\n'*FILE_CONTENT_MIN_LINES
SPECS_LLAMA_3_2 = getSpecifications(Model.LLAMA_3_2.value)
SPECS_QWEN_2_5_CODER = getSpecifications(Model.QWEN_2_5_CODER.value)


class TestHistoryExport(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open, read_data=HISTORY)
    @patch(f'{SUT_PREFIX}.getFilePath', return_value=TEST_EXPORT_OUTPUT_DIR)
    @patch(f'{SUT_PREFIX}.createFolder')
    @patch(f'{SUT_PREFIX}.sanitize_filepath', side_effect=lambda x: x)
    @patch(f'{SUT_PREFIX}.zipfile.ZipFile')
    def test_exportHistory(self, mock_zipfile, mock_sanitize, mock_create_folder, mock_getFilePath, mock_open):
        result = exportHistory(USER, HISTORY)
        self.assertTrue(result.is_absolute())
        mock_create_folder.assert_called_once_with(TEST_EXPORT_OUTPUT_DIR+'/')
        mock_open.assert_called_with(TEST_EXPORT_OUTPUT_DIR+'/README.md', 'w')
        self.assertEqual(mock_open.call_count, 2)
        mock_zipfile.assert_called_once_with(
            TEST_EXPORT_OUTPUT_DIR+'.zip', 'w', zipfile.ZIP_DEFLATED)

    def test_answerDir(self):
        content = "Sample sentence. Additional text."
        result = _answerDir(SPECS_LLAMA_3_2, content)
        self.assertEqual(result, "Sample sentence/")

    @patch(f'{SUT_PREFIX}.createFolder')
    def test_moveCodeBlocksToFiles(self, mock_create_folder):
        zip_mock = MagicMock(spec=zipfile.ZipFile)
        content = f'Sample content with *test_code.py*\n```python\n{
            FILE_CONTENT}```'
        result = _moveCodeBlocksToFiles(
            SPECS_LLAMA_3_2, zip_mock, TEST_EXPORT_OUTPUT_DIR, ANSWER_DIR, content)
        self.assertIn("[test_code.py]", result)
        mock_create_folder.assert_called_once_with(TEST_EXPORT_OUTPUT_DIR)
        zip_mock.write.assert_called_once()

    def test_byPattern_with_matching_pattern(self):
        zip_mock = MagicMock(spec=zipfile.ZipFile)
        content = f"**test_code.py**\n```python\n{FILE_CONTENT}```"
        result = _moveCodeBlocksToFiles(
            SPECS_LLAMA_3_2, zip_mock, TEST_EXPORT_OUTPUT_DIR, ANSWER_DIR, content)
        self.assertIn("[test_code.py]", result)
        zip_mock.write.assert_called_once()

    # @patch('threading.Timer')
    @patch(f'{SUT_PREFIX}.shutil.rmtree')
    @patch(f'{SUT_PREFIX}.os.remove')
    def test_cleanFuture(self, mock_remove, mock_rmtree):
        def asserts():
            mock_rmtree.assert_called_once_with('./' + TEST_EXPORT_OUTPUT_DIR)
            mock_remove.assert_called_once_with(ZIP_FILE_PATH)
        _cleanFuture(TEST_EXPORT_OUTPUT_DIR, ZIP_FILE_PATH, 0)
        Timer(interval=0, function=asserts).start()


if __name__ == '__main__':
    unittest.main()
