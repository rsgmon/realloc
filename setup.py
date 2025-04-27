from setuptools import setup, find_packages

setup(
    name="portmgr",
    version="0.1.0",
    description="A modular Python library for multi-account portfolio trade allocation",
    author="Your Name",
    author_email="you@example.com",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'portfolio-cli=core.__main__:main',
        ],
    },
    extras_require={
        'dev': [
            'pytest',
            'pytest-cov',
            'black',
            'flake8',
        ]
    },
    tests_require=[
        'pytest',
        'pytest-cov',
        'hypothesis',
    ],
)
