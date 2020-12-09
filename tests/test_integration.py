from io import StringIO
from unittest import mock

import pytest
from django.core.management import call_command, CommandError


def call_command_fixtures(*args, **kwargs):
    out = StringIO()
    call_command('fixtures', *args, stdout=out, stderr=StringIO(), **kwargs)
    return out.getvalue()


def test_call_command_without_args():
    """Test that calling the command without args returns proper error."""
    with pytest.raises(CommandError, match="Error: command must be specified. Choose from: 'fill' or 'flush'"):
        call_command_fixtures()


def test_call_command_all_arg():
    """Test that calling the command with only '--all' arg returns all available fixtures."""
    result = call_command_fixtures('--all')

    assert (
        result
        == './manage.py fixtures fill profiles - Fill the database with fake user profiles.\n'
           './manage.py fixtures flush profiles - Remove all user profiles.\n✨ Found 2 fixture(s)\n'
    )


@mock.patch('django_fixtures_command.management.commands.fixtures.all_fixtures')
def test_call_command_all_arg_when_there_are_no_fixtures(mock_all_fixtures):
    """Test that calling '--all' arg when there are no fixtures returns proper message."""
    mock_all_fixtures.return_value = iter(())

    result = call_command_fixtures('--all')
    assert result == '✨ Found 0 fixture(s)\n'


@pytest.mark.django_db
def test_call_command_fill():
    """Test that calling the subcommand 'fill' runs proper callable in a transaction."""
    result = call_command_fixtures('fill', 'profiles')
    assert result == '🤞 Loading fill_profiles fixture...\n🚀 Fixture loaded successfully\n'


def test_call_command_fill_without_arg():
    """Test that calling the subcommand 'fill' without arg returns proper error."""
    match_msg = "Error: fixture name argument must be specified. Show all available fixtures with '--all' option"
    with pytest.raises(CommandError, match=match_msg):
        call_command_fixtures('fill')


def test_call_command_fill_with_invalid_arg():
    """Test that calling the subcommand 'fill' with fixture that isn't defined returns proper error."""


def test_call_command_flush_without_arg():
    """Test that calling the subcommand 'flush' without arg returns proper error."""
    match_msg = "Error: fixture name argument must be specified. Show all available fixtures with '--all' option"
    with pytest.raises(CommandError, match=match_msg):
        call_command_fixtures('flush')


def test_call_command_flush_with_invalid_arg():
    """Test that calling the subcommand 'flush' with fixture that isn't defined returns proper error."""
    exec_msg = "Error: unrecognized fixture fixture_that_is_not_defined. Show all available fixtures with '--all' option"
    with pytest.raises(CommandError, match=exec_msg):
        call_command_fixtures("flush", "fixture_that_is_not_defined")


@pytest.mark.parametrize(
    "call_args, expected",
    [
        (("flush", "profiles", "--all"), "Error: unrecognized arguments: --all"),
        (("fill", "profiles", "--all"), "Error: unrecognized arguments: --all"),
        (("flush", "--all"), "Error: unrecognized arguments: --all"),
        (("fill", "--all"), "Error: unrecognized arguments: --all"),
    ],
)
def test_call_command_all_arg_after_fill_or_flush_subcommands(call_args, expected):
    """Test that calling '--all' arg can't be used with a subcommand."""
    with pytest.raises(CommandError, match=expected):
        call_command_fixtures(*call_args)
