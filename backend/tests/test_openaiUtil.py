from typing import List
import unittest
from unittest.mock import patch
from openai.pagination import SyncPage
from openai.types import Model
from service.openaiUtil import getModels


class TestGetModels(unittest.TestCase):

    @staticmethod
    def mock_SyncPage(mock, data: List[Model]):
        mock.models.list.return_value = SyncPage[Model](object='', data=data)

    @patch('service.openaiUtil.openAICli')
    def test_getModels(self, mock_openAICli):
        self.mock_SyncPage(mock_openAICli, [Model(id='model1', object='model', created=1, owned_by='x'),
                                            Model(id='model2', object='model', created=1, owned_by='x')])
        self.assertEqual(getModels(), ['model1', 'model2'])

    @patch('service.openaiUtil.openAICli')
    def test_getModels_no_data(self, mock_openAICli):
        self.mock_SyncPage(mock_openAICli, [])
        with self.assertRaises(Exception):
            getModels()


if __name__ == '__main__':
    unittest.main()
