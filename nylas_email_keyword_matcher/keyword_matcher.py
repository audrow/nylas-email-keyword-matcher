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
        if self.is_keyword(keyword):
            raise RuntimeError(f"Keyword '{keyword}' already added")
        self._keywords.append(keyword.lower())

    @property
    def keywords(self) -> typing.List[str]:
        return self._keywords

    def __str__(self):
        return ', '.join([f'"{k}"' for k in self.keywords])

    def is_keyword(self, text: str):
        return text.lower() in self.keywords

    def get_match_at_beginning(self, text: str) -> str:
        pattern = "|".join(self.keywords)
        match = re.match(pattern, text.strip(), flags=re.I)
        if match:
            return match.group()
        else:
            raise NoKeywordFound(f"No keyword found in '{text}'")