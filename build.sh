#!/bin/bash

# NLTK verilerini indir
python -m nltk.downloader punkt
python -m nltk.downloader stopwords
python -m nltk.downloader wordnet

# TextBlob verilerini indir
python -c "import textblob; textblob.download_corpora()"

# Veritabanını oluştur
python -c "from app import app; from models import db; app.app_context().push(); db.create_all()"
