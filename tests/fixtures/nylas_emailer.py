import pytest
from nylas import APIClient

from nylas_email_keyword_matcher.nylas_emailer import \
    NylasEmailer, NoEmailReplyError
from nylas_email_keyword_matcher.nylas_context_manager import \
    NylasContextManager


@pytest.fixture
def random_subject():
    return 'test subject - ' + NylasEmailer.get_random_string()


@pytest.fixture
def random_body_content():
    return NylasEmailer.get_random_string()


@pytest.fixture
def random_body_html_content(random_body_content):
    return f'<html><a>{random_body_content}</a></html>'


@pytest.fixture
def real_nylas_emailer():
    return NylasEmailer(NylasContextManager())


@pytest.fixture
def to_email():
    return APIClient().account['email_address']


@pytest.fixture()
def send_email(
        real_nylas_emailer,
        random_subject,
        random_body_content,
        random_body_html_content,
        to_email):
    real_nylas_emailer.send(
        random_subject,
        random_body_html_content,
        to_email,
    )

    yield real_nylas_emailer, random_subject, random_body_content, random_body_html_content

    try:
        real_nylas_emailer.mark_reply_as_read(random_subject)
    except NoEmailReplyError:
        pass


