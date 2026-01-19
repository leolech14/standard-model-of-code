from setuptools import setup, find_packages

setup(
    name="collider",
    version="2.3.0",
    description="Collider - Standard Model of Code Analysis & Visualization",
    author="Standard Model Team",
    packages=find_packages(),
    py_modules=["cli"],
    install_requires=[
        "tree-sitter>=0.20.0",
        "tree-sitter-python>=0.20.0",
        "networkx>=3.0",
        "matplotlib",
        "numpy",
    ],
    entry_points={
        "console_scripts": [
            "collider=cli:main",
        ],
    },
    include_package_data=True,
    python_requires=">=3.8",
)
