from api.api import app
import pytest
from api.flaskUtil import setResponseKO_internal__


EXCEPTED_EXCEPTION_STR = ["ServiceException: ('Mocked exception', Exception('cause'))", 'ValidationException: Required fields not informed: model, user, question, history, ability', 'MethodNotAllowed: 405 Method Not Allowed: The method is not allowed for the requested URL.', 'Exception: parent', 'Exception: cause']


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.app_context()
    with app.test_client() as client:
        yield client


# Test cases
def test_setResponseKO():
    try:
        raise Exception("parent") from Exception("cause")
    except Exception as ex:
        assert EXCEPTED_EXCEPTION_STR == setResponseKO_internal__(ex)
