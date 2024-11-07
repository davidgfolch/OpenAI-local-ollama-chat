from threading import Timer
import unittest
from unittest.mock import patch, mock_open, MagicMock, ANY
import zipfile
import json

from service.langchain.historyExport import MIN_LINES, PATTERN_FILE_FILENAME_CODE, exportHistory, _answerDir, _moveCodeBlocksToFiles, _byPattern, cleanFuture

# Constants for test
USER = 'test_user'
HISTORY = 'test_history'
OUT_DIR = 'test_output/'
ANSWER_DIR = 'answer_dir/'
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
                "type": "human"
            }
        }
    ]))
    @patch(f'{SUT_PREFIX}.getFilePath', return_value='fake_path')
    @patch(f'{SUT_PREFIX}.createFolder')
    @patch(f'{SUT_PREFIX}.sanitize_filepath', side_effect=lambda x: x)
    @patch(f'{SUT_PREFIX}.zipfile.ZipFile')
    def test_exportHistory(self, mock_zipfile, mock_sanitize, mock_create_folder, mock_getFilePath, mock_open):
        # zip_mock = MagicMock(spec=zipfile.ZipFile)
        # mock_zipfile.return_value.__enter__.return_value = zip_mock
        result = exportHistory(USER, HISTORY)
        self.assertTrue(result.is_absolute())
        mock_create_folder.assert_called_once_with('fake_path/')
        mock_open.assert_called_with('fake_path/README.md', 'w')
        self.assertEqual(mock_open.call_count, 2)
        mock_zipfile.assert_called_once_with(
            'fake_path.zip', 'w', zipfile.ZIP_DEFLATED)
        # zip_mock.write.assert_any_call(README_PATH, 'fake_path/README.md')
        # mock_zipfile.write.assert_called_once_with('fake_path/README.md', 'fake_path/README.md')

    def test_answerDir_with_human_type(self):
        content = "Sample sentence. Additional text."
        answer_dir = ""
        result = _answerDir("human", answer_dir, content)
        self.assertEqual(result, "Sample sentence/")

    def test_answerDir_with_non_human_type(self):
        content = "Sample sentence."
        answer_dir = ""
        result = _answerDir("bot", answer_dir, content)
        self.assertEqual(result, "")

    @patch(f'{SUT_PREFIX}.createFolder')
    def test_moveCodeBlocksToFiles(self, mock_create_folder):
        zip_mock = MagicMock(spec=zipfile.ZipFile)
        content = f'Sample content with *File: test_code.py*\n```python\n{FILE_CONTENT}```'
        result = _moveCodeBlocksToFiles(
            zip_mock, OUT_DIR, ANSWER_DIR, content, "human")
        self.assertIn("[test_code.py]", result)
        mock_create_folder.assert_called_once_with(OUT_DIR+'/'+ANSWER_DIR)
        zip_mock.write.assert_called_once()

    def test_byPattern_with_matching_pattern(self):
        zip_mock = MagicMock(spec=zipfile.ZipFile)
        content = f"**File: test_code.py**\n```python\n{FILE_CONTENT}```"
        result = _byPattern(PATTERN_FILE_FILENAME_CODE,
                            zip_mock, OUT_DIR, ANSWER_DIR, content, "human")
        self.assertIn("[test_code.py]", result)
        zip_mock.write.assert_called_once()

    @patch('threading.Timer')
    @patch('shutil.rmtree')
    @patch('os.remove')
    def test_cleanFuture(self, mock_remove, mock_rmtree, mock_timer):
        def asserts():
            mock_timer.assert_called_once_with(
                interval=0, function=ANY, args=(OUT_DIR, ZIP_FILE_PATH))
            mock_rmtree.assert_called_once_with('./' + OUT_DIR)
            mock_remove.assert_called_once_with(ZIP_FILE_PATH)
        cleanFuture(OUT_DIR, ZIP_FILE_PATH, 0)
        Timer(interval=0, function=asserts).start()


if __name__ == '__main__':
    unittest.main()
