import typing
import re


class NoKeywordFound(Exception):
    pass


class KeywordMatcher:
    def __init__(
            self,
            *keywords: str,
    ):
        self._keywords = []
        self.add_keywords(*keywords)

    def add_keywords(self, *keywords: str):
        for keyword in keywords:
            self.add_keyword(keyword)

    def add_keyword(self, keyword: str):
        if keyword in self:
            raise RuntimeError(f"Keyword '{keyword}' already added")
        self._keywords.append(keyword.lower())

    @property
    def keywords(self) -> typing.List[str]:
        return self._keywords

    def __str__(self):
        return ', '.join([f'"{k}"' for k in self.keywords])

    def __contains__(self, item):
        return item.lower() in self.keywords

    def has_keyword(
            self, text: str, is_at_beginning_only: bool = True) -> bool:
        try:
            self.get_first_keyword(
                text=text, is_at_beginning_only=is_at_beginning_only)
            return True
        except NoKeywordFound:
            return False

    def get_first_keyword(
            self, text: str, is_at_beginning_only: bool = True) -> str:
        pattern = '(' + '|'.join(self.keywords) + ')'
        if is_at_beginning_only:
            pattern = '^' + pattern
        match = re.search(pattern, text.strip(), flags=re.I)
        if match:
            return match.group()
        else:
            raise NoKeywordFound(f"No keyword found in '{text}'")
