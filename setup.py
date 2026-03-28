from setuptools import setup, find_packages

setup(
    name="app_institucional",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flet>=0.21.0",
        "openai>=1.14.0",
        "PyMuPDF>=1.24.0",
        "SQLAlchemy>=2.0.0",
        "python-dotenv>=1.0.0",
        "pytesseract>=0.3.10",
        "Pillow>=10.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "black>=24.0.0",
            "isort>=5.13.0",
            "mypy>=1.9.0",
        ],
    },
)
