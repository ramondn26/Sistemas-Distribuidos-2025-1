from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

app = FastAPI()

# Carrega tokenizer lento (sentencepiece)
tokenizer = AutoTokenizer.from_pretrained(
    "cardiffnlp/twitter-xlm-roberta-base-sentiment",
    use_fast=False
)
model = AutoModelForSequenceClassification.from_pretrained(
    "cardiffnlp/twitter-xlm-roberta-base-sentiment"
)
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model=model,
    tokenizer=tokenizer
)

class Query(BaseModel):
    text: str

@app.post("/analyze")
async def analyze(q: Query):
    result = sentiment_analyzer(q.text)[0]
    mapping = {
        "positive": "POSITIVO",
        "neutral":  "NEUTRO",
        "negative": "NEGATIVO"
    }
    sentimento = mapping.get(result["label"], result["label"])
    confianca   = round(result["score"], 4)
    return {
        "sentimento": sentimento,
        "confianca":  confianca
    }
