from fastapi import FastAPI

server = FastAPI()


@server.get("/hello")
def get():
    return "Hello, World"
