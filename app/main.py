from fastapi import FastAPI

app = FastAPI(title="Collab Board")

@app.get("/")
def home():
    return {"message": "Collab Board is running"}