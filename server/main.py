from dataclasses import dataclass

from fastapi import FastAPI, Request, Response
import pymongo


server = FastAPI()

PAGE_SIZE = 5

@dataclass
class Token:
    exp: int
    
    def generate(key: bytearray):

    
# TODO: memory leak
async def get_collection(name: str):
    client = pymongo.MongoClient("mongodb://root:password@localhost:27017")
    db = client["public_api_data_db"]
    if name not in db.list_collection_names():
        return None
    
    return db[name]

@server.get("/api/v1/auth/token")
async def get(request: Request):
    return {"req": [request.client.host, request.client.port]} 

# TODO: group the routes together
@server.get("/api/v1/categories")
async def get(page: int, response: Response):
    if page < 1:
        response.status_code = 400
        return {"status": "400", "message": "Bad request"}

    collection = await get_collection("categories")
    data = collection.find_one()["categories"]

    start = ((page - 1) * PAGE_SIZE)
    end   = start + PAGE_SIZE
    data = data[start:end]
    if len(data) == 0:
        response.status_code = 404
        return None

    return {"data": data}
    
@server.get("/api/v1/apis/entry")
async def get(page: int, category: str, response: Response):
    if page < 1:
        response.status_code = 400
        return {"status": "400", "message": "Bad request"}
   
    collection = await get_collection(category)
    if collection is None:
        response.status_code = 400
        return {"status": "400", "message": f"non existent category {category}"}

    doc = collection.find_one()
    start = ((page - 1) * PAGE_SIZE)
    end   = start + PAGE_SIZE
    data = doc["data"][start : end]

    if len(data) == 0:
        response.status_code = 404
        return None

    return {"data": data}

