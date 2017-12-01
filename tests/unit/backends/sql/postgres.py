"""Define SQL statements for Postgres tests."""


CREATE_RECORD = (
    'INSERT INTO "{namespace}"."{table}" (\n'
    '   "{a}", "{b}", "{c}"\n'
    ')\n'
    'VALUES($1, $2, $3)\n'
    'RETURNING *;'
)
CREATE_I18N_RECORD = (
    'WITH inserted AS (\n'
    '   INSERT INTO "{namespace}"."{table}" (\n'
    '       "{a}"\n'
    '   )\n'
    '   VALUES($1)\n'
    '   RETURNING *;\n'
    ')\n'
    'INSERT INTO "{namespace}"."{table}_i18n" (\n'
    '   "{b}", "{c}", "locale", "{key}"\n'
    ')\n'
    'SELECT $2, $3, $4, inserted."{key}" FROM inserted\n'
    'RETURNING *;'
)
DELETE_RECORD_BY_KEY_FIELD = (
    'DELETE FROM "{namespace}"."{table}" '
    'WHERE ("{column}"=$1);'
)
DELETE_RECORD_BY_KEY_INDEX = (
    'DELETE FROM "{namespace}"."{table}" '
    'WHERE ("{a}"=$1 AND "{b}"=$2);'
)
DELETE_I18N_RECORD_BY_KEY_FIELD = (
    'DELETE FROM "{namespace}"."{table}_i18n" '
    'WHERE ("{column}"=$1);\n'
    'DELETE FROM "{namespace}"."{table}" '
    'WHERE ("{column}"=$1);'
)
GET_FIRST_RECORD_BY_KEY_FIELD = (
    'SELECT "{a}", "{b}"\n'
    'FROM "{namespace}"."{table}"\n'
    'ORDER BY "{a}" ASC\n'
    'LIMIT 1;'
)
GET_LAST_RECORD_BY_KEY_FIELD = (
    'SELECT "{a}", "{b}"\n'
    'FROM "{namespace}"."{table}"\n'
    'ORDER BY "{a}" DESC\n'
    'LIMIT 1;'
)
GET_RECORD_BY_KEY_FIELD = (
    'SELECT "{a}", "{b}"\n'
    'FROM "{namespace}"."{table}"\n'
    'WHERE ("{a}"=$1)\n'
    'LIMIT 1;'
)
GET_I18N_RECORD_BY_KEY_FIELD = (
    'SELECT "{a}", "{b}", i18n."{c}", i18n."{d}"\n'
    'FROM "{namespace}"."{table}"\n'
    'LEFT JOIN "{namespace}"."{i18n_table}" i18n '
    'ON (i18n."{a}"="{a}" AND i18n."locale"=$1)\n'
    'WHERE ("{a}"=$2)\n'
    'LIMIT 1;'
)
GET_RECORD_BY_KEY_INDEX = (
    'SELECT "{a}", "{b}", "{c}"\n'
    'FROM "{namespace}"."{table}"\n'
    'ORDER BY "{a}" ASC, "{b}" ASC\n'
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
    'SELECT "{a}", "{b}" AS "{b_as}"\n'
    'FROM "{namespace}"."{table}"\n'
    'WHERE ("{a}"=$1)\n'
    'LIMIT 1;'
)


def make_backend():
    """Create new Postgres backend."""
    from orb.backends.sql.postgres import Postgres
    return Postgres()
