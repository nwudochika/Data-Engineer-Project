from fastapi import FastAPI
from faker import Faker
import random
from datetime import datetime, timedelta

app = FastAPI()
fake = Faker()

@app.get("/")
def root():
    return {"message": "Fake Weather API is running"}

@app.get("/fake_weather")
def fake_weather(days: int = 10):
    """
    Generates fake daily weather data, similar to Delhi climate dataset
    """
    today = datetime.today()
    data = []
    for i in range(days):
        date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        entry = {
            "date": date,
            "meantemp": round(random.uniform(5, 40), 2),
            "humidity": round(random.uniform(20, 100), 1),
            "wind_speed": round(random.uniform(0, 25), 2),
            "meanpressure": round(random.uniform(980, 1025), 2)
        }
        data.append(entry)

    return {"count": len(data), "records": data}
