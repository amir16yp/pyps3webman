from setuptools import setup, find_packages

setup(
    name='ps3webman',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4'
    ],
    author='Amir Y. Perehodnik',
    author_email='i-need-adderall@protonmail.com',  # Replace with your email address
    description='A library designed to control a PS3 using webMAN',
    long_description='''This library provides a Python interface to control a PlayStation 3 console using the webMAN MOD. It allows users to send commands and retrieve information from the PS3 over the network. This is particularly useful for automating tasks or integrating PS3 control into larger systems.''',
    long_description_content_type='text/markdown',  # If your long_description is written in markdown
    url='https://github.com/amir16yp/pyps3webman',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: The Unlicense (Unlicense)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
