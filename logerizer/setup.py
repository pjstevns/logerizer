from setuptools import setup, find_packages

version = '0.1'

setup(
    name='logerizer',
    version=version,
    description="Sanetize network syslog messages",
    long_description="""\
    aggregate messages per host and timestamp, so consecutive
    messages from the same host on the same timestamp are
    concatenated to one single message.
    """,
    classifiers=[],
    keywords='logstash',
    author='Lukkien BV',
    author_email='p.stevens@lukkien.com',
    url='http://www.lukkien.com',
    license='GPLv3',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points=dict(
        console_scripts=[
            'log_proxy = logerizer.proxy:run',
            'tcp_sink = logerizer.sink:run',
        ]
    )
)
