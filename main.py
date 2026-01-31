from fastapi import FastAPI

app = FastAPI(title="FastAPI CRUD - Tasks")

@app.get("/health")
def health():
    return {"ok": True}