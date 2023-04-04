from setuptools import setup

setup(
	name='TradingBot',
	version='0.0.1',
	packages=[''],
	url='https://github.com/GabryDX/TradingBot',
	license='MIT',
	author='Gabriele Nicosanti',
	author_email='heronikostudios@gmail.com',
	description='Python Telegram bot to manage personal stocks',
    install_requires=['python-telegram-bot'],
    dependency_links=['https://github.com/GabryDX/yahoo_fin/']
)
