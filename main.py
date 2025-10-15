from fastapi import FastAPI
import uvicorn
from api.routes.user import user_router


app = FastAPI()
app.include_router(user_router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
