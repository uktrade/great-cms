from setuptools import setup, find_packages


setup(
    name='directory_components',
    version='35.27.0',
    url='https://github.com/uktrade/directory-components',
    license='MIT',
    author='Department for International Trade',
    description='Shared components library for Great services.',
    packages=find_packages(exclude=['tests.*', 'tests', 'scripts', 'demo.*', '*.css.map']),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    include_package_data=True,
    install_requires=[
        'django>=1.11,<3.0a1',
        'beautifulsoup4>=4.6.0,<5.0.0',
        'directory-constants>=20.11.0,<21.0.0',
        'jsonschema>=3.0.1,<4.0.0',
    ],
    extras_require={
        'test': [
            'lorem==0.1.1',
            'ansicolors==1.1.8',
            'codecov==2.1.9',
            'flake8==3.7.8',
            'pytest-cov==2.6.1',
            'pytest-django==3.3.0',
            'pytest-sugar',
            'pytest==3.6.0',
            'requests-toolbelt==0.8.0',
            'requests==2.18.1',
            'twine>=1.11.0,<2.0.0',
            'wheel>=0.31.0,<1.0.0',
            'setuptools>=38.6.0,<39.0.0'
        ],
        'demo': [
            'lorem==0.1.1',
            'django-environ==0.4.5',
            'gunicorn==19.5.0',
            'whitenoise==3.3.1',
            'django-pygments==0.3.0',
        ],
        'janitor': [
            'hvac>=0.9.5,<1.0.0',
            'vulture>=1.0.0,<2.0.0',
            'ansicolors>=1.1.8,<2.0.0',
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
