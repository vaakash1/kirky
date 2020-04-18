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
            'pyx',
            'numpy'
        ],
        zip_safe=False)
