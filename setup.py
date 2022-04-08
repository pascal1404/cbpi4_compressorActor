from setuptools import setup

setup(name='cbpi4_compressorActor',
      version='0.0.1',
      description='CraftBeerPi Plugin for Compressor actors',
      author='Pascal Scholz',
      author_email='pascal1404@gmx.de',
      url='',
      include_package_data=True,
      package_data={
        # If any package contains *.txt or *.rst files, include them:
      '': ['*.txt', '*.rst', '*.yaml'],
      'cbpi4_compressorActor': ['*','*.txt', '*.rst', '*.yaml']},
      packages=['cbpi4_compressorActor'],
     )