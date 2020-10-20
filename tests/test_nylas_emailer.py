import pytest

from nylas_email_keyword_matcher.nylas_emailer import \
    NylasEmailer, NoEmailReplyError


@pytest.mark.uses_nylas_api
@pytest.mark.timeout(60)
def test_send_email(send_email):
    nylas_emailer, subject, content, html_content = send_email
    assert html_content == nylas_emailer.get_reply(subject, timeout=None, is_strip_html=False)
    assert content == nylas_emailer.get_reply(subject, timeout=None, is_strip_html=True)


@pytest.mark.uses_nylas_api
@pytest.mark.timeout(60)
def test_send_email_with_timeout(send_email):
    nylas_emailer, subject, _, _ = send_email
    with pytest.raises(TimeoutError):
        nylas_emailer.get_reply(subject, timeout=0)
    with pytest.raises(TimeoutError):
        nylas_emailer.get_reply(subject, timeout=2)


@pytest.mark.uses_nylas_api
@pytest.mark.timeout(60)
def test_mark_as_read(send_email):
    nylas_emailer, subject, _, _ = send_email
    nylas_emailer.get_reply(subject, timeout=None)

    assert nylas_emailer.is_reply(subject)
    nylas_emailer.mark_reply_as_read(subject)
    assert not nylas_emailer.is_reply(subject)


@pytest.mark.uses_nylas_api
@pytest.mark.timeout(60)
def test_error_on_no_reply(real_nylas_emailer):
    subject = 'fake subject'
    with pytest.raises(NoEmailReplyError):
        assert not real_nylas_emailer.is_reply(subject)
        real_nylas_emailer.mark_reply_as_read(subject)


def test_get_random_string():
    for length in [10, 21, 50]:
        str1 = NylasEmailer.get_random_string(length=length)
        str2 = NylasEmailer.get_random_string(length=length)
        assert str1 != str2
        assert len(str1) == len(str2) == length
