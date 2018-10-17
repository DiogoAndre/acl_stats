#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0', 'requests', 'colorama']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Diogo André de Assumpção",
    author_email='diogo.aa@protonmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Quickly gather access-lists stats from Cisco ASA Firewalls",
    entry_points={
        'console_scripts': [
            'acl_stats=acl_stats.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='acl_stats',
    name='acl_stats',
    packages=find_packages(include=['acl_stats']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/diogoandre/acl_stats',
    version='0.1.3',
    zip_safe=False,
)
