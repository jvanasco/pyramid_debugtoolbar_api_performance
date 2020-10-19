"""pyramid_debugtoolbar_api_performance installation script.
"""
import os
from setuptools import setup
from setuptools import find_packages

# store version in the init.py
import re

with open(
    os.path.join(
        os.path.dirname(__file__), "pyramid_debugtoolbar_api_performance", "__init__.py"
    )
) as v_file:
    VERSION = re.compile(r'.*__VERSION__ = "(.*?)"', re.S).match(v_file.read()).group(1)

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.rst")).read()

requires = [
    "pyramid",
    "pyramid_debugtoolbar>=4.0",
    "six",
]
tests_require = [
    "pytest",
]
testing_extras = tests_require + []

setup(
    name="pyramid_debugtoolbar_api_performance",
    author="Jonathan Vanasco",
    author_email="jonathan@findmeon.com",
    url="https://github.com/jvanasco/pyramid_debugtoolbar_api_performance",
    version=VERSION,
    description="performance csv exporting for pyramid_debugtoolbar",
    keywords="web pyramid",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Framework :: Pyramid",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    long_description=README,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=tests_require,
    extras_require={
        "testing": testing_extras,
    },
    test_suite="tests",
)
