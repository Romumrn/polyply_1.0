from setuptools import find_packages, setup

setup(
    name='polyply',
    version='0.1.1',
    author='Fabian Grünewald',
    author_email='f.grunewald@rug.nl',
    packages=find_packages(),
    include_package_data=True,
    scripts=['bin/polyply.gen_itp', ],
    license='Apache 2.0',
    description='Tool for generating MARTINI Polymer itps and structures',
    long_description=open('README.md').read(),
    install_requires=['numpy', 'scipy','networkx','tqdm'],
)