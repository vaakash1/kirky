from setuptools import setup

setup(name='kirky',
        version='0.9',
        description='A Kirchhoff Graph generator',
        url='http://github.com/erebuseternal/kirky',
        author='erebuseternal',
        author_email='marcelsanders96@gmail.com',
        license='None',
        packages=['kirky'],
        install_requires=[
            'future',
            'matplotlib==3.2.1',
            'networkx==2.4',
            'numpy==1.20.0',
            'pyx',
            'sklearn==0.0',
            'tqdm',
        ],
        zip_safe=False)
