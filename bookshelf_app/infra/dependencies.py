from fastapi import Depends
from sqlalchemy.orm import Session

from bookshelf_app.api.auth.service import AuthService, TokenUserAppModel, oauth2_scheme
from bookshelf_app.api.book_with_reviews.service import BookWithReviewsService
from bookshelf_app.api.books.service import BookService
from bookshelf_app.api.reviews.service import BookReviewService
from bookshelf_app.api.tags.service import TagService
from bookshelf_app.infra.db.auth import SqlUserRepository
from bookshelf_app.infra.db.book_with_reviews import SqlBookWithQueryService
from bookshelf_app.infra.db.books import SqlBookRepository
from bookshelf_app.infra.db.database import get_session
from bookshelf_app.infra.db.reviews import SqlBookReviewRepository
from bookshelf_app.infra.db.tags import SqlTagRepository
from bookshelf_app.infra.other.crypt import CryptService


def get_tag_service(session: Session = Depends(get_session)) -> TagService:
    return TagService(SqlTagRepository(session))


def get_auth_service(session: Session = Depends(get_session)) -> AuthService:
    return AuthService(SqlUserRepository(session), CryptService())


def get_book_service(session: Session = Depends(get_session)) -> BookService:
    return BookService(SqlBookRepository(session), SqlTagRepository(session))


def get_book_review_service(session: Session = Depends(get_session)) -> BookReviewService:
    return BookReviewService(SqlBookReviewRepository(session), SqlBookRepository(session))


def get_book_with_review_service(session: Session = Depends(get_session)) -> BookWithReviewsService:
    return BookWithReviewsService(SqlBookWithQueryService(session))


def get_admin_dependency(
    session: Session = Depends(get_session), token: str = Depends(oauth2_scheme)
) -> TokenUserAppModel:
    serve = AuthService(SqlUserRepository(session), CryptService())
    return serve.get_admin_user(token)


def get_user_dependency(
    session: Session = Depends(get_session), token: str = Depends(oauth2_scheme)
) -> TokenUserAppModel:
    serve = AuthService(SqlUserRepository(session), CryptService())
    return serve.get_current_user(token)
