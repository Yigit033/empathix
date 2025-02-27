from transformers import pipeline

def test_sentiment_model():
    # Hugging Face duygu analizi modelini yükle
    sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    
    # Test metinleri
    test_texts = [
        "I love this product, it's amazing!",  # Pozitif
        "This is the worst experience ever.",   # Negatif
        "The weather is nice today.",           # Pozitif
        "I'm very disappointed with the service.",  # Negatif
        "It's okay, nothing special."           # Nötr (model ikili sınıflandırma yaptığı için pozitif veya negatif olarak sınıflandırılacak)
    ]
    
    # Her metin için duygu analizi yap
    for text in test_texts:
        result = sentiment_analyzer(text)
        sentiment = result[0]['label']
        confidence = result[0]['score'] * 100
        
        print(f"Metin: '{text}'")
        print(f"Duygu: {sentiment}")
        print(f"Güven Skoru: %{confidence:.2f}")
        print("-" * 50)

if __name__ == "__main__":
    print("Duygu Analizi Modeli Testi Başlıyor...")
    test_sentiment_model()
    print("Test tamamlandı.")
