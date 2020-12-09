from unittest import mock

import pytest
from django_fixtures_command.management.commands.fixtures import (
    convert_path_to_module_name,
    isfixture, Fixture, get_fixture,
)


def fill_profiles():
    """Fixture callable fixture."""
    pass


def flush_profiles():
    """Fixture callable fixture."""
    pass


@pytest.mark.parametrize(
    'fixture, expected',
    [
        (Fixture('fill_profiles', fill_profiles), 'fill'),
        (Fixture('flush_profiles', flush_profiles), 'flush'),
    ],
)
def test_fixture_prefix(fixture, expected):
    """Test that prefix property returns proper prefix."""
    assert fixture.prefix == expected


@pytest.mark.parametrize(
    'fixture, expected',
    [
        (Fixture('fill_profiles', fill_profiles), 'profiles'),
        (Fixture('flush_campaigns', flush_profiles), 'campaigns'),
    ],
)
def test_fixture_raw_name(fixture, expected):
    """Test that raw_name property returns just fixture name, without prefix and infix."""
    assert fixture.raw_name == expected


def test_fixture_repr():
    """Test Fixture repr()"""
    fixture = Fixture('fill_profiles', fill_profiles)

    assert repr(fixture) == f'Fixture(name={fixture.name}, callable={repr(fixture.callable)})'


def test_fixture_str():
    """Test Fixture str()"""
    def fill_callable_without_doc():
        pass

    def flush_callable_with_doc():
        """Doc"""
        pass

    assert str(Fixture('fill_callable_without_doc', fill_callable_without_doc)) == 'fill callable_without_doc'
    assert str(Fixture('flush_callable_with_doc', flush_callable_with_doc)) == 'flush callable_with_doc - Doc'


test_fixture_fill_profiles = Fixture('fill_profiles', fill_profiles)


@pytest.mark.parametrize(
    'return_value, expected',
    [
        (iter(()), None),
        (iter((test_fixture_fill_profiles, Fixture('flush_profiles', flush_profiles))), test_fixture_fill_profiles)
    ]
)
@mock.patch('django_fixtures_command.management.commands.fixtures.all_fixtures')
def test_get_fixture(mock_all_fixtures, return_value, expected):
    mock_all_fixtures.return_value = return_value

    assert get_fixture('fill', 'profiles') == expected


@pytest.mark.parametrize(
    "path, expected",
    [
        ('tests/testapp/app2/fixtures.py', 'tests.testapp.app2.fixtures'),
        ('fixtures.py', 'fixtures'),
    ],
)
def test_convert_path_to_module_name(path, expected):
    """Test that function converts a path to a module name properly."""
    assert convert_path_to_module_name(path) == expected


def test_isfixture():
    """Test that isfixture checks properly if a callable if can be treated as a fixture."""
    def fill_example():
        pass

    def flush_example():
        pass

    def not_fixture_example():
        pass

    class fill_valid_fixture:
        pass

    class invalid_fixture1:
        __slots__ = ('__call__',)

        def __cal__(self):
            pass

    class invalid_fixture2:
        pass

    assert isfixture(fill_example) is True
    assert isfixture(flush_example) is True
    assert isfixture(fill_valid_fixture) is True
    assert isfixture(not_fixture_example) is False
    assert isfixture(invalid_fixture1) is False
    assert isfixture(invalid_fixture2) is False
