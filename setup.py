from distutils.core import setup

setup(
    # Application name:
    name="playlist",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="Paul D.Smith",
    author_email="paul_d_smith@hotmail.com",

    # Packages
    package_dir="src",
    packages=["playlist"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="https://github.com/papadeltasierra/playlist",

    #
    # license="LICENSE.txt",
    description="Randomized MP3 pplaylist generator.",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
        "eyeD3",
    ],
)