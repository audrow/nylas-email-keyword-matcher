import pytest
from nylas.client.errors import NylasError

from nylas_email_keyword_matcher.nylas_context_manager import \
    NylasContextManager


@pytest.fixture
def nylas_api_mock(mocker):
    return mocker.patch(
        'nylas_email_keyword_matcher.nylas_context_manager.APIClient')


def make_nylas_manager():
    return NylasContextManager(
        app_id='foo', app_secret='bar', access_token='baz')


def test_init_tries_nylas_api_client(nylas_api_mock):
    assert not nylas_api_mock.called

    # Calls APIClient to test on init
    nylas_manager = make_nylas_manager()
    assert nylas_api_mock.called

    # Calls APIClient on each context created
    for i in range(2, 10):
        with nylas_manager as nylas:
            assert nylas == nylas_manager._api_client
            assert nylas_manager._api_client is not None
        assert nylas_api_mock.call_count == i
        assert nylas_manager._api_client is None

    # Calls APIClient on each valid check
    for i in range(10, 20):
        assert nylas_manager.is_valid_client()
        assert nylas_api_mock.call_count == i


def test_initial_test_fails(nylas_api_mock):
    nylas_api_mock.side_effect = Exception
    with pytest.raises(NylasError):
        make_nylas_manager()


def test_context_fails(nylas_api_mock):
    nylas_manager = make_nylas_manager()
    nylas_api_mock.side_effect = Exception
    with pytest.raises(NylasError):
        with nylas_manager:
            pass
