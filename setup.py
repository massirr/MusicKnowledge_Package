from setuptools import setup, find_packages

setup(name='MusicKnowledge-Package',
      version='1.0',
      description='the exam package',
      author='Irakoze',
      license='MIT',
      packages=find_packages(include=['MusicKnowledge']),
      install_requires=['reportlab', 'bs4', 'requests', 're', 'spotipy', 'spotipy.oauth2', ]
      # leave [] empty if no packages required     
)