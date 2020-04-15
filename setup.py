from setuptools import find_packages, setup

from toga import __version__, __description__


def main():
    with open('requirements.txt') as f:
        requirements = f.read().splitlines()

    setup(
        name='TOGA',
        description=__description__,
        version=__version__,
        packages=find_packages(),
        entry_points={
            'console_scripts': [
                'toga-client = toga.cli.toga_client:main',
                'toga-server = toga.cli.toga_server:main'
            ],
        },
        include_package_data=True,
        package_data={},
        install_requires=requirements
    )


if __name__ == '__main__':
    main()
