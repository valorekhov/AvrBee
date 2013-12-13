from distutils.core import setup

packages=[
    'arduinoXbeeProgrammer', 
    'arduinoXbeeProgrammer.tests', 
]

setup(
    name='Arduino XBee Programmer',
    version='1.1.0',
    author='Val Orekhov',
    author_email='valorekhov@gmail.com',
    packages=packages,
    scripts=[],
    url='http://code.google.com/p/python-xbee/',
    license='LICENSE.txt',
    description='Arduino tool for programming remote boards through XBee S2/ZB radios running in API and AT modes',
    long_description=open('README.txt').read(),
    requires=['serial', 'xbee'],
    provides=packages,
)
