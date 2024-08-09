#TODO: Change it to run on this ip : 144.24.97.63
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, workers=4, reload=True)