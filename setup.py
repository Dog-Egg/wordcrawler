from setuptools import setup

setup(
    name='wordcrawler',
    version='0.0.1',
    entry_points={
        'console_scripts': [
            'wordcrawler = wordcrawler.cli:main',
        ]
    },
    install_requires=[
        'scrapy',
        'pydash',
        'click',
        'tabulate'
    ]
)
