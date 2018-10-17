from setuptools import setup, find_packages

setup(
    name='TradeShop',
    version='1.0.2',
    description='Processes a trade request into a trade list.',
    author='Ryeland Gongora',
    author_email='rsgmon@gmail.com',
    packages=find_packages(exclude=('test_data_generator') ),
    python_requires='~=3.3'
)

