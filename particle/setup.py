from setuptools import setup, find_packages

# Legacy fallback for tools that don't support pyproject.toml.
# Canonical configuration lives in pyproject.toml.
setup(
    name="collider",
    version="4.0.0",
    description="Collider - Standard Model of Code Analysis & Visualization",
    author="Leonardo Lech",
    author_email="leonardo.lech@gmail.com",
    python_requires=">=3.10",
    packages=find_packages(where="."),
    py_modules=["cli"],
    install_requires=[
        "tree-sitter>=0.20.0",
        "tree-sitter-python>=0.20.0",
        "tree-sitter-javascript>=0.20.0",
        "tree-sitter-typescript>=0.20.0",
        "tree-sitter-go>=0.20.0",
        "tree-sitter-rust>=0.20.0",
        "tree-sitter-java>=0.20.0",
        "networkx>=3.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "jinja2>=3.1.0",
        "libcst>=1.0.0",
    ],
    extras_require={
        "graphrag": [
            "lancedb>=0.6.13",
            "litellm>=1.80.0",
            "sentence-transformers>=3.2.1",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "collider=cli:main",
        ],
    },
    include_package_data=True,
)
