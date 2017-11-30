"""Define SQL statements for Postgres tests."""


DELETE_RECORD_BY_KEY_FIELD = (
    'DELETE FROM "{namespace}"."{table}" '
    'WHERE ("{column}"=$1);'
)
DELETE_RECORD_BY_KEY_INDEX = (
    'DELETE FROM "{namespace}"."{table}" '
    'WHERE ("{column_a}"=$1 AND "{column_b}"=$2);'
)
DELETE_I18N_RECORD_BY_KEY_FIELD = (
    'DELETE FROM "{namespace}"."{table}_i18n" '
    'WHERE ("{column}"=$1);\n'
    'DELETE FROM "{namespace}"."{table}" '
    'WHERE ("{column}"=$1);'
)
GET_FIRST_RECORD = (
    'SELECT "{column_a}", "{column_b}"\n'
    'FROM "{namespace}"."{table}"\n'
    'ORDER BY "{column_a}" ASC\n'
    'LIMIT 1;'
)
GET_LAST_RECORD = (
    'SELECT "{column_a}", "{column_b}"\n'
    'FROM "{namespace}"."{table}"\n'
    'ORDER BY "{column_a}" DESC\n'
    'LIMIT 1;'
)
GET_RECORD_BY_KEY_FIELD = (
    'SELECT "{column_a}", "{column_b}"\n'
    'FROM "{namespace}"."{table}"\n'
    'WHERE ("{column_a}"=$1)\n'
    'LIMIT 1;'
)
GET_RECORD_BY_KEY_INDEX = (
    'SELECT "{column_a}", "{column_b}", "{column_c}"\n'
    'FROM "{namespace}"."{table}"\n'
    'ORDER BY "{column_a}" ASC, "{column_b}" ASC\n'
    'LIMIT 1;'
)
GET_RECORD_COUNT = (
    'SELECT COUNT(*) AS "count"\n'
    'FROM "{namespace}"."{table}";'
)
GET_FILTERED_RECORD_COUNT = (
    'SELECT COUNT(*) AS "count"\n'
    'FROM "{namespace}"."{table}"\n'
    'WHERE ("{column}"=$1 OR "{column}"=$2);'
)
GET_RECORD_WITH_COLUMN_AS = (
    'SELECT "{column_a}", "{column_b}" AS "{column_b_as}"\n'
    'FROM "{namespace}"."{table}"\n'
    'WHERE ("{column_a}"=$1)\n'
    'LIMIT 1;'
)
INSERT_RECORD = (
    'INSERT INTO "{namespace}"."{table}"\n'
    'SET ("{column_a}", "{column_b}", "{column_c}")\n'
    'VALUES $1, $2, $3;'
)
INSERT_I18N_RECORD = (
    'INSERT INTO "{namespace}"."{table}"\n'
    'SET ("{column_a}")\n'
    'VALUES $1;\n'
    'INSERT INTO "{namespace}"."{table}_i18n"\n'
    'SET ("locale", "{column_b}", "{column_c}")\n'
    'VALUES $2, $3, $4;'
)


def make_backend():
    """Create new Postgres backend."""
    from orb.backends.sql.postgres import Postgres
    return Postgres()
