import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from bookshelf_app.api.auth import router as auth
from bookshelf_app.api.books import router as books
from bookshelf_app.api.reviews import router as reviews
from bookshelf_app.api.tags import router as tags
from bookshelf_app.helper import serve_spa_app as spa
from bookshelf_app.helper.custom_error_handler import handle_custom_error
from bookshelf_app.helper.http_middleware import HttpRequestMiddleware

app = FastAPI()
app.include_router(tags.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(books.router, prefix="/api")
app.include_router(reviews.router, prefix="/api")

app.add_middleware(HttpRequestMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.mount("/", StaticFiles(directory="frontend/build",html = True), name="frontend")
# mount spa apps
PATH_SPA_DIR = "bookshelf_app/frontend/dist"
app = spa.serve_spa_app(app, PATH_SPA_DIR)

app = handle_custom_error(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
