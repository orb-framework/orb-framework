"""Tests for the Index class."""


def test_index_definition():
    """Basic definition of an index."""
    from orb import Index

    index = Index()
    assert index.field_names == []
    assert index.flags == Index.Flags(0)
    assert index.name == ''
    assert index.code == ''


def test_index_definition_with_flags():
    """Test to initialize an index with flag options."""
    from orb import Index

    index = Index(flags=Index.Flags.Key)
    assert index.test_flag(Index.Flags.Key) is True
    assert index.test_flag(Index.Flags.Unique) is False


def test_index_definition_with_flag_set():
    """Test to initialize an index with a set of flag options."""
    from orb import Index

    index = Index(flags={'Key'})
    assert index.test_flag(Index.Flags.Key) is True
    assert index.test_flag(Index.Flags.Unique) is False
