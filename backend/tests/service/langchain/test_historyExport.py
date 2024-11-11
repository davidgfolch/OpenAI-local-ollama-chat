from threading import Timer
import unittest
from unittest.mock import patch, mock_open, MagicMock
import zipfile
import json

from service.langchain.historyExport import PATTERN_FILENAME_CODE, MIN_LINES, exportHistory, _answerDir, _moveCodeBlocksToFiles, _byPattern, _cleanFuture

# Constants for test
USER = 'test_user'
HISTORY = 'test_history'
TEST_EXPORT_OUTPUT_DIR = 'test_export_output'
ANSWER_DIR = 'answer_dir'
ZIP_FILE_PATH = 'test_history.zip'
CONTENT_FILE = 'test_file.py'
CONTENT = """## Sample Content for Testing"""
SUT_PREFIX = 'service.langchain.historyExport'
FILE_CONTENT = 'print(\'Hello\')\n'*MIN_LINES


class TestHistoryExport(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps([
        {
            "data": {
                "content": CONTENT,
                "type": "not-human"
            }
        }
    ]))
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
        mock_zipfile.assert_called_once_with(TEST_EXPORT_OUTPUT_DIR+'.zip', 'w', zipfile.ZIP_DEFLATED)

    def test_answerDir_with_human_type(self):
        content = "Sample sentence. Additional text."
        result = _answerDir(content)
        self.assertEqual(result, "Sample sentence/")

    @patch(f'{SUT_PREFIX}.createFolder')
    def test_moveCodeBlocksToFiles(self, mock_create_folder):
        zip_mock = MagicMock(spec=zipfile.ZipFile)
        content = f'Sample content with *test_code.py*\n```python\n{FILE_CONTENT}```'
        result = _moveCodeBlocksToFiles(
            zip_mock, TEST_EXPORT_OUTPUT_DIR, ANSWER_DIR, content, "human")
        self.assertIn("[test_code.py]", result)
        mock_create_folder.assert_called_once_with(TEST_EXPORT_OUTPUT_DIR)
        zip_mock.write.assert_called_once()

    def test_byPattern_with_matching_pattern(self):
        zip_mock = MagicMock(spec=zipfile.ZipFile)
        content = f"**test_code.py**\n```python\n{FILE_CONTENT}```"
        result = _byPattern(PATTERN_FILENAME_CODE,
                            zip_mock, TEST_EXPORT_OUTPUT_DIR, ANSWER_DIR, content, "human")
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
