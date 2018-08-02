from setuptools import setup, find_packages
import sys, os

version = '1.0'

import sys
if sys.version_info < (3,4):
    sys.exit('Sorry, Python < 3.4 is not supported')

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('gronk/static')

setup(name='gronk',
      version=version,
      description="Tornado based miniwiki",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='web',
      author='Jim Finnis',
      author_email='jim.finnis@gmail.com',
      url='http://pale.org.uk/mine/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      install_requires=[
          # -*- Extra requirements: -*-
        'tornado>=5',
        'passlib>=1.7','markdown'
      ],
      entry_points= {
        'console_scripts': [
            'gronk = gronk.__main__:main'
        ]
      },
      package_data = {
        'gronk': {'':extra_files}
      },
      )
