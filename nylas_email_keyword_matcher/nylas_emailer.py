import string
import random
import re
import time
from typing import Optional
from datetime import datetime, timedelta

from nylas_email_keyword_matcher.nylas_context_manager import \
    NylasContextManager


class MultipleMatchingEmailThreadsError(Exception):
    pass


class NoEmailReplyError(Exception):
    pass


class NoThreadFoundError(Exception):
    pass


class NylasEmailer:
    def __init__(
            self,
            nylas_context_manager: NylasContextManager,
    ):
        self._nylas_context_manager = nylas_context_manager

    def send(self, subject: str, body: str, *to: str):
        with self._nylas_context_manager as nylas:
            draft = nylas.drafts.create()
            draft.subject = subject
            draft.body = body
            draft.to = [{'name': address, 'email': address} for address in to]
            draft.send()

    def get_reply(
            self,
            subject: str,
            timeout: Optional[int] = None,
            is_strip_html: bool = True,
    ) -> str:
        """
        Get the reply to an email with a given subject.

        :param subject:
            The subject of the email you are expecting a reply to
        :param timeout:
            This timeout has three modes:
                * (Pass in 0) Run once and raise an error if there is no reply
                * (Pass in any positive integer) Run keep running until there
                  is a reply or raise an exception if a specified amount of
                  time has elapsed
                * (Pass in :code:`None`) Run keep running until there is a
                  reply
        :param is_strip_html:
            This removes HTML tags and replaces :code:`<br>` tags
            with new line characters
        :return:
        """
        self._wait_for_reply(subject, timeout)
        thread_id = self._get_reply_thread_id(subject)
        return self._get_body(thread_id, is_strip_html)

    def _wait_for_reply(self, subject: str, timeout: Optional[int] = None):
        if timeout is None:
            while not self.is_reply(subject):
                time.sleep(1)
        else:
            if timeout < 0:
                raise ValueError(f'Timeout must be non negative: {timeout}')
            if timeout == 0 and self.is_reply(subject):
                pass
            else:
                timeout_time = datetime.now() + timedelta(seconds=timeout)
                while not self.is_reply(subject):
                    if timeout_time < datetime.now():
                        raise TimeoutError(
                            "Didn't receive email reply to subject "
                            f"'{subject}' before timing out")
                    time.sleep(1)

    def is_reply(self, subject: str):
        try:
            self._get_reply_thread_id(subject)
            return True
        except NoEmailReplyError:
            return False

    def mark_reply_as_read(self, subject: str):
        try:
            thread_id = self._get_reply_thread_id(subject)
            self._mark_as_read(thread_id)
        except NoEmailReplyError as e:
            raise NoEmailReplyError("No unread email reply to mark as read") from e

    def _get_reply_thread_id(self, subject: str) -> str:
        with self._nylas_context_manager as nylas:
            threads = nylas.threads.where(subject=subject, unread=True)
            num_threads = len(threads.all())
            if num_threads == 1:
                return threads.first()['id']
            elif num_threads == 0:
                raise NoEmailReplyError()
            elif num_threads > 1:
                raise MultipleMatchingEmailThreadsError("The reply is ambiguous")
            else:
                raise RuntimeError("There should never be a negative number of threads")

    def _mark_as_read(self, thread_id: str):
        with self._nylas_context_manager as nylas:
            try:
                thread = nylas.threads.get(thread_id)
            except ConnectionError as e:
                raise NoThreadFoundError(f"No thread with id '{thread_id}' found") from e
            thread.mark_as_read()

    def _get_body(self, thread_id: str, is_strip_html=True) -> str:
        with self._nylas_context_manager as nylas:
            try:
                thread = nylas.threads.get(thread_id)
            except ConnectionError as e:
                raise NoThreadFoundError(f"No thread with id '{thread_id}' found") from e

            last_message = thread.messages[0]
            html = last_message['body']
            if is_strip_html:
                # replace <br> with new lines then remove html tags
                return re.sub('<[^<]+?>', '', re.sub('<br>', '\n', html))
            else:
                return html

    @staticmethod
    def get_random_string(length=6):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for _ in range(length))
