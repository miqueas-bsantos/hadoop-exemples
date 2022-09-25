from datetime import datetime
from typing import Optional
from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status
from model import Schemas
from typing import List
from db import db
from aws import S3
import pandas as pd
from io import StringIO

router = APIRouter()

@router.get("/lowest-movie-rated", description="Retorna os filmes com pior avaliação")
async def lowest_movie_rated():
    response = {}
    try:
        file = S3(p_bucket="senac-datalake-miqueas").get_object(p_key="script/lowest_movie_rated.csv")
        df = pd.read_csv(StringIO(file))
        response = {
            "statusCode": 200,
            "data": df.to_dict(orient='records'),
            "messages": ""
        }
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=500,
            detail=response
        )

@router.get("/highest-movie-rated", description="Retorna os filmes com melhor avaliação")
async def highest_movie_rated():
    response = {}
    try:
        file = S3(p_bucket="senac-datalake-miqueas").get_object(p_key="script/highest_movie_rated.csv")
        df = pd.read_csv(StringIO(file))
        response = {
            "statusCode": 200,
            "data": df.to_dict(orient='records'),
            "messages": ""
        }
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=500,
            detail=response
        )        