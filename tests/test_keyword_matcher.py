import pytest

from nylas_email_keyword_matcher.keyword_matcher import \
    KeywordMatcher, NoKeywordFound


def test_add_keywords_individually_after_init(unique_keywords):
    km = KeywordMatcher()
    assert len(km.keywords) == 0
    for index in range(len(unique_keywords)):
        km.add_keyword(unique_keywords[index])
        assert len(km.keywords) == index + 1


def test_add_keywords_in_bulk_after_init(unique_keywords):
    km = KeywordMatcher()
    assert len(km.keywords) == 0
    km.add_keywords(*unique_keywords)
    assert len(km.keywords) == len(unique_keywords)


def test_init_with_keywords(unique_keywords):
    km = KeywordMatcher(*unique_keywords)
    assert len(km.keywords) == len(unique_keywords)


def test_raise_error_on_duplicate_keywords(nonunique_keywords):
    with pytest.raises(RuntimeError):
        KeywordMatcher(*nonunique_keywords)
    with pytest.raises(RuntimeError):
        km = KeywordMatcher()
        km.add_keywords(*nonunique_keywords)


def test_str_method(keyword_matcher):
    assert type(str(keyword_matcher)) is str


def test_is_keyword(keyword_matcher, unique_keywords):
    for k in unique_keywords:
        assert k in keyword_matcher
        assert k in keyword_matcher
        assert k.upper() in keyword_matcher
        assert k.capitalize() in keyword_matcher
    for k in unique_keywords:
        assert "bar" + k + "baz" not in keyword_matcher


def test_match_keyword_in_text_body(keyword_matcher):
    text = 'Here is some text'
    keyword1 = 'FOO'
    for keyword in ['keyword', 'MULTIPLE WORD KEYWORD']:
        assert keyword not in keyword_matcher
        keyword_matcher.add_keyword(keyword)

        for content in [
            f'{text}',
            f'{text*3}',
        ]:
            with pytest.raises(NoKeywordFound):
                keyword_matcher.get_first_keyword(
                    content, is_at_beginning_only=False)

        for content in [
            keyword,
            f'{keyword} {keyword1}',
            f'{keyword} {text}',
            f'{text*3} {keyword} {text}',
            f'\n\t   {keyword} {text}',
        ]:
            assert keyword == keyword_matcher.get_first_keyword(
                content, is_at_beginning_only=False)


def test_match_at_beginning_of_text_body(keyword_matcher):
    text = 'Here is some text'
    is_at_beginning_only = True
    for keyword in ['keyword', 'MULTIPLE WORD KEYWORD']:
        assert keyword not in keyword_matcher
        keyword_matcher.add_keyword(keyword)

        for content in [
            f'{text}',
            f'{text} {keyword}',
            f'a {keyword}',
        ]:
            assert not keyword_matcher.has_keyword(
                content, is_at_beginning_only=is_at_beginning_only)
            with pytest.raises(NoKeywordFound):
                keyword_matcher.get_first_keyword(
                    content, is_at_beginning_only=is_at_beginning_only)

        for content in [
            keyword,
            f'{keyword} {keyword}',
            f'{keyword} {text}',
            f'{keyword} {keyword} {text}',
            f'\n\t   {keyword} {text}',
        ]:
            assert keyword_matcher.has_keyword(
                content, is_at_beginning_only=is_at_beginning_only)
            assert keyword == keyword_matcher.get_first_keyword(
                content, is_at_beginning_only=is_at_beginning_only)


def test_match_keyword_with_multiple_keywords_in_text_body(keyword_matcher):
    text = 'Here is some text'
    keyword1 = 'FOO'
    keyword2 = 'BAR BAZ'
    is_at_beginning_only = False

    for keyword in [keyword1, keyword2]:
        assert keyword not in keyword_matcher
        keyword_matcher.add_keyword(keyword)

    for content in [
        f'{text}',
        f'{text*3}',
    ]:
        assert not keyword_matcher.has_keyword(
            content, is_at_beginning_only=is_at_beginning_only)
        with pytest.raises(NoKeywordFound):
            keyword_matcher.get_first_keyword(
                content, is_at_beginning_only=is_at_beginning_only)

    assert keyword1 == keyword_matcher.get_first_keyword(
        f'{keyword1} {keyword2} {keyword2}',
        is_at_beginning_only=is_at_beginning_only)
    assert keyword2 == keyword_matcher.get_first_keyword(
        f'{keyword2} {keyword1} {keyword1}',
        is_at_beginning_only=is_at_beginning_only)
