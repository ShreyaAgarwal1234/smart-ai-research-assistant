from fastapi import FastAPI

# FastAPI instance **must** be called “app”
app = FastAPI()

@app.get("/")
def read_root():
    return {"msg": "Environment is working!"}
