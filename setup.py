# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

long_desc = '''
This package contains the plsqldomain Sphinx extension.

This extension provides a PL/SQL domain for Sphinx.

'''

requires = ['Sphinx>=1.0']

setup(
    name='sphinxcontrib-plsqldomain',
    version='0.1.0',
    url='https://github.com/felipebz/sphinxcontrib-plsql',
    license='BSD',
    author='Felipe Zorzo',
    author_email='felipe at felipezorzo dot com dot br',
    description='Sphinx "plsqldomain" extension',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
)
