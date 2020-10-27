import pytest

from nylas_email_keyword_matcher.email_keyword_matcher import \
    NylasEmailKeywordMatcher
from nylas_email_keyword_matcher import exceptions


@pytest.fixture()
def mock_nylas_email_keyword_matcher(mocker, keyword_matcher):
    nylas_emailer_mock = mocker.MagicMock()
    email_matcher = NylasEmailKeywordMatcher(
        nylas_emailer=nylas_emailer_mock,
        keyword_matcher=keyword_matcher,
    )
    return email_matcher, nylas_emailer_mock, keyword_matcher


def test_keywords_property(mock_nylas_email_keyword_matcher):
    email_matcher, _, keyword_matcher = \
        mock_nylas_email_keyword_matcher
    assert email_matcher.keywords == keyword_matcher.keywords


def test_send_email(mock_nylas_email_keyword_matcher):
    email_matcher, nylas_emailer_mock, keyword_matcher = \
        mock_nylas_email_keyword_matcher

    subject = 'my subject'
    message = 'my message'
    recipients = ['a@b.c', 'd@e.f', 'h@i.j']

    assert not nylas_emailer_mock.send.called
    for i in range(len(recipients)):
        to = recipients[:i+1]
        email_matcher._send_email(
            subject,
            message,
            *to,
        )
        assert nylas_emailer_mock.send.called
        assert nylas_emailer_mock.send.call_args.args == \
               (subject, message, *to)


def test_send_keywords_email(mock_nylas_email_keyword_matcher):
    email_matcher, nylas_emailer_mock, keyword_matcher = \
        mock_nylas_email_keyword_matcher

    subject = 'my subject'
    message = 'my message'
    recipients = ['a@b.c', 'd@e.f', 'h@i.j']

    assert not nylas_emailer_mock.send.called
    for i in range(len(recipients)):
        to = recipients[:i+1]
        email_matcher._send_keyword_email(
            subject,
            message,
            *to,
        )
        out_message = nylas_emailer_mock.send.call_args.args[1]
        assert message in out_message
        for keyword in keyword_matcher.keywords:
            assert keyword in out_message


def test_get_response_valid(mock_nylas_email_keyword_matcher):
    email_matcher, nylas_emailer_mock, keyword_matcher = \
        mock_nylas_email_keyword_matcher

    for keyword in keyword_matcher.keywords:
        nylas_emailer_mock.get_reply.return_value = keyword + ' other text'
        response = email_matcher.get_response(
            'my subject', is_keyword_at_beginning_of_text_only=True)
        assert response == keyword


def test_get_response_invalid(mock_nylas_email_keyword_matcher):
    email_matcher, nylas_emailer_mock, keyword_matcher = \
        mock_nylas_email_keyword_matcher

    for keyword in ['foo', 'bar', 'baz', 'woah derr', 'bla bla bla']:
        assert keyword not in keyword_matcher.keywords
        nylas_emailer_mock.get_reply.return_value = keyword + ' other text'
        with pytest.raises(exceptions.NoKeywordFound):
            email_matcher.get_response(
                'my subject', is_keyword_at_beginning_of_text_only=True)


def test_run_once_no_error(mock_nylas_email_keyword_matcher):
    email_matcher, nylas_emailer_mock, keyword_matcher = \
        mock_nylas_email_keyword_matcher

    keyword = keyword_matcher.keywords[0]
    nylas_emailer_mock.get_reply.return_value = keyword + ' other text'

    assert not nylas_emailer_mock.send.called
    assert not nylas_emailer_mock.get_reply.called
    assert not nylas_emailer_mock.mark_reply_as_read.called

    reply = email_matcher._run_once('my subject', 'my message', 'foo@bar.baz')
    assert reply == keyword

    assert nylas_emailer_mock.send.called
    assert nylas_emailer_mock.get_reply.called
    assert nylas_emailer_mock.mark_reply_as_read.called


def test_run_once_no_keyword(mock_nylas_email_keyword_matcher):
    email_matcher, nylas_emailer_mock, keyword_matcher = \
        mock_nylas_email_keyword_matcher

    keyword = 'foo'
    assert keyword not in keyword_matcher.keywords
    nylas_emailer_mock.get_reply.side_effect = exceptions.NoKeywordFound

    assert not nylas_emailer_mock.send.called
    assert not nylas_emailer_mock.get_reply.called
    assert not nylas_emailer_mock.mark_reply_as_read.called

    email_matcher._run_once('my subject', 'my message', 'foo@bar.baz')

    assert nylas_emailer_mock.send.call_count == 2
    assert nylas_emailer_mock.get_reply.called
    assert nylas_emailer_mock.mark_reply_as_read.called


def test_send_email_then_wait_to_process_reply(
        mock_nylas_email_keyword_matcher, mocker):
    email_matcher, nylas_emailer_mock, keyword_matcher = \
        mock_nylas_email_keyword_matcher
    keyword = keyword_matcher.keywords[0]
    run_once_patch = mocker.patch(
        'nylas_email_keyword_matcher.email_keyword_matcher.'
        'NylasEmailKeywordMatcher._run_once')
    run_once_patch.side_effect = [None, None, keyword]

    assert keyword == email_matcher.send_email_then_wait_to_process_reply(
        'my subject', 'my message', 'a@b.c')

    assert run_once_patch.call_count == 3
