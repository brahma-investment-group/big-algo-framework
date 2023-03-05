from setuptools import setup

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='big_algo_framework',
    version='1.0.0',
    packages=['big_algo_framework', 'big_algo_framework.big', 'big_algo_framework.brokers', 'big_algo_framework.data',
              'big_algo_framework.strategies'],
    url='https://github.com/brahma-investment-group/big-algo-framework',
    license='MIT',
    author='Nagabrahmam Mantha',
    author_email='info@brahmainvestmentgroup.ca',
    description='Python trading algorithm connected to various brokers',
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Issue Tracker": "https://github.com/brahma-investment-group/big-algo-framework/issues",
    },
    python_requires='>=3.6',
    install_requires=[
        'discord_webhook',
        'ib_insync',
        'numpy',
        'pandas',
        'polygon',
        'python_dateutil',
        'requests',
        'selenium',
        'tda-api',
        'tweepy',
        'yfinance'],

    keywords='finance trading equities stocks bonds futures options research data markets interactive brokers td '
             'ameritrade polygon algorithm automation')