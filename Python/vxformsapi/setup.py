from setuptools import setup

setup(
    name='vxformsapi',
    version='0.1.0',
    packages=['vxformsapi'],
    install_requires=['requests', 'pandas'],
    url='https://github.com/M9-Calibre/BD_API_Materials',
    license='',
    author='Lucius Vinicius',
    author_email='luciusviniciusf@ua.pt',
    description='API for the VxForms Material Database.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
    ],
)