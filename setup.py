from setuptools import setup, find_packages

setup(
    name="reversal-autotheme",
    version="1.0.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "Pillow>=9.0.0",
        "numpy>=1.20.0"
    ],
    entry_points={
        "console_scripts": [
            "reversal-autotheme=reversal_autotheme.cli:main",
        ],
    },
)
