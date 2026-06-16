# pylint: disable=unused-argument
# pylint: disable=broad-exception-caught

import os

import alembic.config
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

os.environ.setdefault("ENV_FILE", os.getenv("INTEGRATION_ENV_FILE", ".env.test"))

from bookshelf_app import main
from bookshelf_app.infra.db.database import get_session

alembicArgs = [
    "--raiseerr",
    "upgrade",
    "head",
]


def is_database_ready(docker_ip):
    """データベース起動待ち
    接続を試みて、Exceptionが発生しなくなったらコンテナー起動済みとする
    SQLAlchemyが接続できることをDB非依存なSELECTで試す
    """
    try:
        for session in get_session():
            session.execute(text("SELECT 1"))
            # migration start
            print("start migration")
            alembic.config.main(argv=alembicArgs)
            print("end migration")
        return True
    except Exception as e:
        print(e)
        return False


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    compose_file = os.getenv("INTEGRATION_DOCKER_COMPOSE_FILE", "test_env/docker-compose-integration.yml")
    return os.path.join(str(pytestconfig.rootdir), compose_file)


@pytest.fixture(scope="session")
def database_service(docker_ip, docker_services):
    """Docker database service 起動待ち"""
    docker_services.wait_until_responsive(timeout=40.0, pause=0.5, check=lambda: is_database_ready(docker_ip))


@pytest.fixture(scope="session")
def integration_client():
    return TestClient(main.app)


@pytest.fixture(scope="session")
def docker_compose_project_name() -> str:
    """Generate a project name using the current process PID. Override this
    fixture in your tests if you need a particular project name."""

    # to avoid creating duplicate images, return fix name
    return os.getenv("INTEGRATION_DOCKER_COMPOSE_PROJECT_NAME", "pytest-integration_1")
