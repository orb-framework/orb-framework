"""Define model fixtures."""
import pytest


@pytest.fixture
def user_model():
    """Define User model object and return it."""
    from orb import Model, Field, Collector

    class User(Model):
        id = Field()
        username = Field()
        manager = Field()
        employees = Collector()

    return User


@pytest.fixture
def make_users(user_model):
    """Generate users for the given names."""
    def _make_users(*names):
        out = [
            user_model(state={'id': i + 1, 'username': name})
            for i, name in enumerate(names)
        ]
        return out[0] if len(out) == 1 else out
    return _make_users
