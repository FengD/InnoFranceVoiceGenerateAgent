from setuptools import setup, find_packages

setup(
    name="qwen3-tts-inno-france",
    version="1.0.0",
    author="Inno France",
    author_email="contact@innofrance.com",
    description="A product-level implementation of Qwen3-TTS with voice design and cloning capabilities",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/innofrance/qwen3-tts-inno-france",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "qwen-tts",
        "torch>=2.6.0",
        "soundfile>=0.12.0",
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "flask>=2.0.0",
        "flask-cors>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "qwen3-tts-inno=app.cli:main",
        ],
    },
)