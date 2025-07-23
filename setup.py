"""
Setup script for Code Change Summarizer.
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="code-change-summarizer",
    version="0.1.0",
    author="Code Summarizer Team",
    author_email="team@codesummarizer.dev",
    description="A tool to analyze and summarize code changes from git diffs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/code-change-summarizer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "code-summarizer=code_summarizer.cli:main",
            "summarize-changes=code_summarizer.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "code_summarizer": ["*.py"],
    },
    keywords="git diff analysis code review summarization",
    project_urls={
        "Bug Reports": "https://github.com/your-org/code-change-summarizer/issues",
        "Source": "https://github.com/your-org/code-change-summarizer",
        "Documentation": "https://github.com/your-org/code-change-summarizer#readme",
    },
)