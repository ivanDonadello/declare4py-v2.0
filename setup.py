from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\\n" + fh.read()

setup(
    name="declare4py",
    version='{{VERSION_PLACEHOLDER}}',
    author="Ivan Donadello, Fabrizio Maria Maggi, Francesco Riva",
    author_email="donadelloivan@gmail.com, maggi@inf.unibz.it, Francesco.Riva@unibz.it",
    description="Python library to perform discovery, conformance checking and query checking of DECLARE constraints.",
    url = "https://github.com/ivanDonadello/Declare4Py",
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(include=['Declare4Py*']),
    include_package_data=True,
    install_requires=['numpy', 'pandas', 'pm4py', 'matplotlib', 'boolean.py', 'clingo', 'ltlf2dfa'],
    keywords=['python', 'bpm', 'declare', 'process-mining', 'rule-mining', 'business-process-management', 'declarative-process-models'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Natural Language :: English",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows"
    ]
)
