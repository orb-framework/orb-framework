"""Tests for the Field class."""


def test_field_definition():
    """Test defining a field."""
    from orb import Field

    f = Field(name='name')
    assert f.name == 'name'
    assert f.code == 'name'
    assert f.label == 'Name'
    assert f.flags == f.Flags(0)
    assert f.default is None


def test_field_label_generation():
    """Test default label options."""
    from orb import Field

    f = Field(name='first_name')
    assert f.name == 'first_name'
    assert f.label == 'First Name'


def test_field_label_override():
    """Test setting label values."""
    from orb import Field

    f = Field(name='first_name', label='First')
    assert f.name == 'first_name'
    assert f.label == 'First'
    f.label = 'First name'
    assert f.label == 'First name'


def test_field_flags():
    """Test setting field flags on initialization."""
    from orb import Field

    f = Field(flags=Field.Flags.Unique | Field.Flags.Required)
    assert f.test_flag(Field.Flags.Unique)
    assert f.test_flag(Field.Flags.Unique | Field.Flags.Required)


def test_field_flags_from_set():
    """Test setting field flags on initialization."""
    from orb import Field

    f = Field(flags={'Unique', 'Required'})
    assert f.test_flag(Field.Flags.Unique)
    assert f.test_flag(Field.Flags.Unique | Field.Flags.Required)


def test_field_code_overrides():
    """Test defining a field with overrides."""
    from orb import Field

    f = Field(name='created_by', code='created_by_id')
    assert f.name == 'created_by'
    assert f.code == 'created_by_id'

    f = Field(name='created_by', code=lambda x: '{}_id'.format(x.name))
    assert f.name == 'created_by'
    assert f.code == 'created_by_id'

    f.code = 'created'
    assert f.code == 'created'


def test_field_default_overrides():
    """Test getting field default override values."""
    from orb import Field

    f = Field(default=1)
    assert f.default == 1

    f = Field(name='created', default=lambda x: x.name)
    assert f.default == 'created'

    f.default = 10
    assert f.default == 10


def test_field_getter_method():
    """Test field getter methods."""
    from orb import Field

    f = Field(name='testing', gettermethod=lambda x: x)
    assert f.gettermethod(f) is f

    @f.getter
    def get_value(field):
        return field.name

    assert f.gettermethod(f) == f.name


def test_field_query_method():
    """Test field query methods."""
    from orb import Field

    f = Field(name='testing', querymethod=lambda x: x)
    assert f.querymethod(f) is f

    @f.query
    def get_value(field):
        return field.name

    assert f.querymethod(f) == f.name


def test_field_setter_method():
    """Test field setter methods."""
    from orb import Field

    f = Field(name='testing', settermethod=lambda x: x)
    assert f.settermethod(f) is f

    @f.setter
    def get_value(field):
        return field.name

    assert f.settermethod(f) == f.name
