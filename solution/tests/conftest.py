from importlib.resources import files
from importlib.resources.abc import Traversable

import pytest

import tests.files
from tests.fixtures.file_loader import ImportLibResourceLoader


@pytest.fixture(scope="session")
def assets_path() -> Traversable:
    return files(tests.files)


@pytest.fixture(scope="session")
def resource_loader(assets_path: Traversable) -> ImportLibResourceLoader:
    return ImportLibResourceLoader(assets_path)
