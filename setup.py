from setuptools import setup

setup(
   name='TradeShop',
   version='1.0',
   description='Processes a trade request into a trade list.',
   author='Ryeland Gongora',
   author_email='rsgmon@gmail.com',
   packages=['pandas'],  #same as name
   install_requires=['pandas', 'numpy'], #external packages as dependencies
)