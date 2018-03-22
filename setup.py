# coding: utf8

from setuptools import setup

setup(name='yandex_pdd',
      version='0.11b',
      description='API Yandex PDD',
      url='http://github.com/zt50tz/yandex-pdd',
      author='Alexeev Nick',
      author_email='n@akolka.ru',
      license='MIT',
      packages=['yandex_pdd'],
      install_requires=[
          'requests',
      ],
      zip_safe=False)
