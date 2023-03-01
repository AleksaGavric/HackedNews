from fastapi import FastAPI

app = FastAPI(
    title="hackednews",
    version="1.0",
    summary="HackerNews Daily Digest",
)


@app.get("/")
def read_root():
    return {"Hello": "World"}
