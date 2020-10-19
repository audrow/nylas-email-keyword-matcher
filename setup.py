from setuptools import setup, find_packages

setup(
    name='NylasEmailKeywordMatcher',
    version='0.0.1',
    url='https://github.com/audrow.git',
    author='Author Name',
    author_email='audrow@hey.com',
    description='Send emails and check the reply for keywords.',
    packages=find_packages(),    
    install_requires=[
        'nylas',
    ],
    tests_require=[
        'pytest',
        'pytest-mock',
    ]
)