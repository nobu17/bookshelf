import uvicorn
from fastapi import FastAPI

from bookshelf_app.api.auth import router as auth
from bookshelf_app.api.tags import router as tags
from bookshelf_app.api.books import router as books
from bookshelf_app.api.reviews import router as reviews
from bookshelf_app.helper import serve_spa_app as spa
from bookshelf_app.helper.custom_error_handler import handle_custom_error
from bookshelf_app.helper.http_middleware import HttpRequestMiddleware

app = FastAPI()
app.include_router(tags.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(books.router, prefix="/api")
app.include_router(reviews.router, prefix="/api")

app.add_middleware(HttpRequestMiddleware)

# app.mount("/", StaticFiles(directory="frontend/build",html = True), name="frontend")
# mount spa apps
path_spa_dir = "bookshelf_app/frontend/build"
app = spa.serve_spa_app(app, path_spa_dir)

app = handle_custom_error(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
