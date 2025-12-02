from fastapi.responses import RedirectResponse

from source.app import app

@app.get("/")
def home():
    return RedirectResponse("/docs")