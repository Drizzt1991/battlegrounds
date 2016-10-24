import pytest

from ._testutil import debug_draw as _debug_draw


@pytest.fixture(scope='session')
def debug_draw():
    return _debug_draw
