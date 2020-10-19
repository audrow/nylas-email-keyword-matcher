import pytest

from nylas_email_keyword_matcher.keyword_matcher import \
    KeywordMatcher, NoKeywordFound


@pytest.fixture
def unique_keywords():
    return ['abc', 'def', 'ghi', 'klm', 'nop']


@pytest.fixture
def nonunique_keywords(unique_keywords):
    out = []
    for keyword in unique_keywords:
        for _ in range(2):
            out.append(keyword)
    return out


@pytest.fixture
def keyword_matcher(unique_keywords):
    return KeywordMatcher(*unique_keywords)


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
        assert keyword_matcher.is_keyword(k)
        assert keyword_matcher.is_keyword(k.lower())
        assert keyword_matcher.is_keyword(k.upper())
        assert keyword_matcher.is_keyword(k.capitalize())
    for k in unique_keywords:
        assert not keyword_matcher.is_keyword("bar" + k + "baz")


def test_match_at_in_text_body(keyword_matcher):
    text = 'Here is some text'
    for keyword in ['keyword', 'MULTIPLE WORD KEYWORD']:
        assert not keyword_matcher.is_keyword(keyword)
        keyword_matcher.add_keyword(keyword)

        with pytest.raises(NoKeywordFound):
            keyword_matcher.get_match_at_beginning(f'{text}')
        with pytest.raises(NoKeywordFound):
            keyword_matcher.get_match_at_beginning(f'{text} {keyword}')

        assert keyword == keyword_matcher.get_match_at_beginning(keyword)
        assert keyword == keyword_matcher.get_match_at_beginning(f'{keyword} {text}')
        assert keyword == keyword_matcher.get_match_at_beginning(f'\n\t   {keyword} {text}')
