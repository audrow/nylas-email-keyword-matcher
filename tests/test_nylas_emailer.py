import os
import pytest
from nylas import APIClient

from nylas_email_keyword_matcher.nylas_emailer import NylasEmailer
from nylas_email_keyword_matcher.nylas_context_manager import NylasContextManager


@pytest.fixture
def random_subject():
    return 'test subject - ' + NylasEmailer.get_random_string()


@pytest.fixture
def random_body_content():
    return NylasEmailer.get_random_string()


@pytest.fixture
def real_nylas_emailer():
    return NylasEmailer(NylasContextManager())


@pytest.fixture
def to_email():
    return APIClient().account['email_address']


@pytest.fixture()
def send_email(
        real_nylas_emailer, random_subject, random_body_content, to_email):
    real_nylas_emailer.send(
        random_subject,
        random_body_content,
        to_email,
    )
    return real_nylas_emailer, random_subject, random_body_content


@pytest.mark.uses_nylas_api
def test_send_email(send_email):
    nylas_emailer, subject, content = send_email
    text = nylas_emailer.get_reply(subject, timeout=None)
    assert text == content


@pytest.mark.uses_nylas_api
def test_send_email_with_timeout(send_email):
    nylas_emailer, subject, content = send_email
    with pytest.raises(TimeoutError):
        nylas_emailer.get_reply(subject, timeout=0)
    with pytest.raises(TimeoutError):
        nylas_emailer.get_reply(subject, timeout=2)


def test_get_random_string():
    for length in [10, 21, 50]:
        str1 = NylasEmailer.get_random_string(length=length)
        str2 = NylasEmailer.get_random_string(length=length)
        assert str1 != str2
        assert len(str1) == len(str2) == length