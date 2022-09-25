from fastapi import FastAPI
from routes import FileRouters
from fastapi.middleware.cors import CORSMiddleware
# Mangum is an adapter for using ASGI applications with 
# AWS Lambda & API Gateway. It is intended to provide
# an easy-to-use, configurable wrapper for any ASGI 
# application deployed in an AWS Lambda function to 
# handle API Gateway requests and responses.
from mangum import Mangum

app = FastAPI(docs_url="/senac-scores/docs", redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
    expose_headers=["*"]
)
app.include_router(FileRouters)
handler = Mangum(app)
    