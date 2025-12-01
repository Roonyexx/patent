from fastapi import FastAPI
import uvicorn
from src.api import auth
from src.api import application
from src.api import patent
from src.api import analytics
from src.api import reference


app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(application.router, prefix="/applications", tags=["applications"])
app.include_router(patent.router, prefix="/patents", tags=["patents"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(reference.router, prefix="/reference", tags=["reference"])


@app.get("/")
async def root():
    """API homepage"""
    return {
        "message": "Welcome to Patent Management System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    uvicorn.run("src.main:app", 
                reload=True, 
                ssl_keyfile="ssl/key.pem", 
                ssl_certfile="ssl/cert.pem"
            )
