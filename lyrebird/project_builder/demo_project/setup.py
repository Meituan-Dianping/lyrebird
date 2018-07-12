from setuptools import setup


setup(
    name='lyrebird-demo',
    version='0.1.0',
    packages=['lyrebird_demo'],
    url='',
    license='',
    author='hbqa',
    author_email='',
    description='',
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
        ],
        'lyrebird_data_handler': [
            'demo = lyrebird_demo.my_handler:MyDataHandler'
        ],
        'lyrebird_web': [
            'demo = lyrebird_demo.my_ui:MyUI'
        ]
    },
    install_requires=[
        'requests'
    ]

)
