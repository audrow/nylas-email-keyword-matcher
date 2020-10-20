import pytest

from nylas_email_keyword_matcher.keyword_matcher import \
    KeywordMatcher


@pytest.fixture
def unique_keywords():
    return [
        'Work it', 'make it', 'do it', 'makes us',
        'Harder', 'better', 'faster', 'stronger'
    ]


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


