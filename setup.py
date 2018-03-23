# coding: utf8

import sys

from setuptools.command.test import test as TestCommand
from setuptools import setup, find_packages, Extension


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='dogerpc',
    version='0.1.4',
    description='A RPC Framework',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author='Timmy',
    author_email='zhu327@gmail.com',
    url='http://github.com/zhu327/doge',
    packages=['doge'] + ["%s.%s" % ('doge', i) for i in find_packages('doge')],
    license='Apache License 2.0',
    keywords=['rpc', 'etcd', 'messagepack', 'gevent', 'microservices'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'mprpc',
        'pyformance',
        'python-etcd',
    ],
    tests_require=[
        'pytest',
    ],
    cmdclass={'test': PyTest}, )
