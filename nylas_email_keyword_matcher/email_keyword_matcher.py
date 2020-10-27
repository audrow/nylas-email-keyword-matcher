from typing import Optional

from nylas_email_keyword_matcher import \
    NylasEmailer, KeywordMatcher, exceptions


class NylasEmailKeywordMatcher:

    def __init__(
            self,
            nylas_emailer: NylasEmailer,
            keyword_matcher: KeywordMatcher,
    ):
        self._emailer = nylas_emailer
        self._keyword_matcher = keyword_matcher

    @property
    def keywords(self):
        return self._keyword_matcher.keywords

    def send_email_then_wait_to_process_reply(
            self,
            subject: str,
            message: str,
            *to: str,
            timeout: Optional[int] = None,
            is_keyword_at_beginning_of_text_only: bool = True,
    ) -> str:
        response = None
        while response is None:
            response = self._run_once(
                subject,
                message,
                *to,
                timeout=timeout,
                is_keyword_at_beginning_of_text_only=(
                    is_keyword_at_beginning_of_text_only)
            )
        return response

    def _run_once(
            self,
            subject: str,
            message: str,
            *to: str,
            timeout: Optional[int] = None,
            is_keyword_at_beginning_of_text_only: bool = True,
    ) -> Optional[str]:
        self._send_keyword_email(subject, message, *to)
        try:
            return self.get_response(
                subject=subject, timeout=timeout,
                is_keyword_at_beginning_of_text_only=(
                    is_keyword_at_beginning_of_text_only
                ))
        except exceptions.NoKeywordFound:
            self._send_email(
                f'ERROR: {subject}',
                (
                    'No keyword found in reply. '
                    'Please reply to the next email with one of '
                    'the keywords.'
                ),
                *to)
        finally:
            self._emailer.mark_reply_as_read(subject)

    def _send_keyword_email(self, subject: str, message: str, *to: str):
        message += f'\nPlease respond with one of the following keywords:' \
                   f'\n\t{self.keywords}'
        self._send_email(subject, message, *to)

    def _send_email(self, subject: str, message: str, *to: str):
        self._emailer.send(subject, message, *to)

    def get_response(
            self,
            subject: str,
            timeout: Optional[int] = None,
            is_keyword_at_beginning_of_text_only: bool = True,
    ) -> str:
        message = self._emailer.get_reply(
            subject=subject, timeout=timeout, is_strip_html=True)

        if self._keyword_matcher.has_keyword(
                message,
                is_at_beginning_only=is_keyword_at_beginning_of_text_only):
            return self._keyword_matcher.get_first_keyword(
                message,
                is_at_beginning_only=is_keyword_at_beginning_of_text_only)
        else:
            raise exceptions.NoKeywordFound
