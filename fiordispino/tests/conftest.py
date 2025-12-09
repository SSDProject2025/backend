import pytest
from django.conf import settings


@pytest.fixture(autouse=True)
def use_tmp_media_root(tmp_path, settings):
    """
    this ficture is automatically called in every test
    set MEDIA_ROOT = tmp_path destroyed at the end of every test
    """
    settings.MEDIA_ROOT = tmp_path / "media"

    # run tests
    yield