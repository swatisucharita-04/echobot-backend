# test.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Hello"}

if __name__ == "__main__":
    try:
        import uvicorn
        print("Starting Uvicorn server...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        print("Uvicorn startup error:", e)
        import traceback
        traceback.print_exc()