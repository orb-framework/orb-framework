"""Define SQL based backend engines for testing."""

from . import postgres

SQL_ENGINES = {
    'postgres': postgres
}
