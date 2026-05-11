from setuptools import setup, find_packages

setup(
    name="watch-youtube",
    version="0.1.0",
    description="YouTube video storyboard generator for Vision LLMs",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "yt-dlp>=2024.3.10",
        "Pillow>=10.3.0",
        "groq>=0.5.0",
        "click>=8.1.7",
        "webvtt-py>=0.4.6",
        "spacy>=3.7.0",
        "scikit-learn>=1.4.0",
    ],
    entry_points={
        "console_scripts": [
            "watch-youtube=watch_youtube.main:cli",
        ],
    },
)
