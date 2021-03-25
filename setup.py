"""pyramid_debugtoolbar_api_performance installation script.
"""
import os
import re
from setuptools import setup
from setuptools import find_packages

# store version in the init.py
HERE = os.path.abspath(os.path.dirname(__file__))

with open(
    os.path.join(HERE, "src", "pyramid_debugtoolbar_api_performance", "__init__.py")
) as v_file:
    VERSION = re.compile(r'.*__VERSION__ = "(.*?)"', re.S).match(v_file.read()).group(1)

long_description = description = "performance csv exporting for pyramid_debugtoolbar"
with open(os.path.join(HERE, "README.rst")) as fp:
    long_description = fp.read()

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
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="web pyramid",
    packages=find_packages(
        where="src",
    ),
    package_dir={"": "src"},
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Framework :: Pyramid",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    zip_safe=False,
    install_requires=requires,
    tests_require=tests_require,
    extras_require={
        "testing": testing_extras,
    },
    test_suite="tests",
)
