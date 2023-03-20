import datetime
import json
import os.path
import typing
from collections import Counter, OrderedDict
from dataclasses import dataclass

_IGNORE_WORDS = {
    "the",
    "to",
    "of",
    "and",
    "by",
    "in",
    "is",
    "for",
    "default",
    "with",
    "be",
    "not",
    "type",
    "will",
    "this",
    "as",
    "that",
    "py",
    "python",
    "or",
    "no",
    "on",
    "it",
    "are",
    "from",
    "name",
    "an",
    "if",
    "you",
}


def _ignore(word: str) -> bool:
    """判断一个单词是否可忽略。"""
    return word.lower() in _IGNORE_WORDS


@dataclass
class _BookData:
    name: str
    words: typing.List
    creation_time: datetime.datetime


class Book:
    BOOKS_DIR = os.path.expanduser('~/.wordcrawler/books')

    def __init__(self, name, meta: dict = None):
        self.name = name
        self.meta = meta or {}
        self._word_counter = Counter()

    @classmethod
    def read_words(cls, name: str, lower=False) -> typing.List[str]:
        """读取单词本内的单词，已过滤可忽略的单词。"""
        book = cls.read_book(name)
        result = OrderedDict()
        for item in sorted(book.words, key=lambda e: e['freq'], reverse=True):
            word: str = item['word']
            if word.lower() not in _IGNORE_WORDS:
                if lower:
                    word = word.lower()
                result.update({word: None})
        return list(result.keys())

    @classmethod
    def get_all(cls):
        try:
            files = os.listdir(cls.BOOKS_DIR)
        except FileNotFoundError:
            files = []
        return [cls.read_book(os.path.splitext(f)[0]) for f in files]

    @classmethod
    def read_book(cls, name):
        with open(cls._get_filepath(name)) as fp:
            data = json.load(fp)
        return _BookData(
            name=name,
            words=data['words'],
            creation_time=datetime.datetime.fromisoformat(data['creation_time'])
        )

    def write_word(self, word):
        """写入单词"""
        self._word_counter.update({word: 1})

    @classmethod
    def _get_filepath(cls, name):
        return os.path.join(cls.BOOKS_DIR, name + '.json')

    def close(self):
        os.makedirs(self.BOOKS_DIR, exist_ok=True)
        with open(self._get_filepath(self.name), mode='w') as fp:
            json.dump({
                'meta': self.meta,
                'creation_time': datetime.datetime.now().isoformat(),
                'words': [
                    dict(word=word, freq=freq) for word, freq in self._word_counter.most_common()
                ],
            }, fp)
