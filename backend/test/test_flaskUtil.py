from api import app
import pytest
from flaskUtil import setResponseKO_internal__


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
        assert ["ServiceException: ('Mocked exception', Exception('cause'))", 'MethodNotAllowed: 405 Method Not Allowed: The method is not allowed for the requested URL.',
                'Exception: parent', 'Exception: cause'] == setResponseKO_internal__(ex)
