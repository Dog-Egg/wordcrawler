#!/usr/bin/env python
from urllib.parse import urlparse, urljoin

import click
from tabulate import tabulate

from . import crawler
from . import storage


@click.group()
def main():
    pass


@main.command()
@click.option('--name', required=True, help='作为结果单词本名称。')
@click.option('--urlpattern', help='允许爬取URL通配表达式。')
@click.argument('url')
def crawl(url, urlpattern, name):
    """爬取网站中的所有单词。"""
    if urlpattern is None:
        result = urlparse(url)
        urlpattern = click.prompt('URLPattern', default=result.hostname + urljoin(result.path, '*'))

    book = storage.Book(name, meta={'url': url, 'urlpattern': urlpattern})
    crawler.run_spider(start_url=url, urlpattern=urlpattern, callback=book.write_word)
    book.close()


@main.command('list')
def list_():
    """列出爬取的单词本。"""
    books = storage.Book.get_all()
    tabledata = [[b.name, len(b.words), b.creation_time.date()] for b in books]
    table = tabulate(tabledata, headers=['Name', 'Count', 'Created'])
    click.echo(table)


@main.command()
@click.option('--sep', default=',')
@click.argument('name')
def echo(sep, name):
    """打印单词本内的单词。"""
    words = storage.Book.read_words(name)
    click.echo(sep.join(words))


if __name__ == '__main__':
    main()
