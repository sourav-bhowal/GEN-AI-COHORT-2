import uvicorn
from .server import app


def main():
    uvicorn.run(app, port=8000, host="0.0.0.0")


main()
