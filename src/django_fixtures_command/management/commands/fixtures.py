import importlib
import inspect
import os
import pathlib
from typing import Any, Iterator, Callable, Final, List, NamedTuple, Literal, Optional

from django.conf import settings
from django.core.management import BaseCommand, CommandParser, CommandError
from django.db import transaction

FILL_CALLABLE_PREFIX: Final[Literal['fill']] = 'fill'
FLUSH_CALLABLE_PREFIX: Final[Literal['flush']] = 'flush'
FIXTURE_CALLABLE_INFIX: Final[Literal['_']] = '_'

FixturePrefix = Literal['fill', 'flush']
FixtureCallable = Callable[[], None]


class Fixture(NamedTuple):
    name: str
    callable: FixtureCallable

    @property
    def prefix(self) -> Optional[FixturePrefix]:
        if self.name.startswith(FILL_CALLABLE_PREFIX):
            return FILL_CALLABLE_PREFIX
        elif self.name.startswith(FLUSH_CALLABLE_PREFIX):
            return FLUSH_CALLABLE_PREFIX
        return None

    @property
    def raw_name(self):
        return self.name[len(self.prefix) + len(FIXTURE_CALLABLE_INFIX):]

    def __repr__(self) -> str:
        return f'Fixture(name={self.name}, callable={repr(self.callable)})'

    def __str__(self) -> str:
        if self.callable.__doc__:
            return f'{self.prefix} {self.raw_name} - {self.callable.__doc__.rstrip()}'
        return f'{self.prefix} {self.raw_name}'


def fixture_files() -> Iterator[pathlib.Path]:
    """Look for fixtures.py files in a Django project. Fixture.py is the file where we define all fixtures."""
    yield from pathlib.Path(settings.BASE_DIR).relative_to(os.getcwd()).glob(f'**/fixtures.py')


def fixture_callables(name: str) -> List[Fixture]:
    """Return all fixtures from the file at the given module name."""
    return [Fixture(*args) for args in inspect.getmembers(importlib.import_module(name), isfixture)]


def isfixture(_object: Any) -> bool:
    """Predicate whether an object is a fixture callable."""
    return (
        callable(_object)
        and hasattr(_object, '__name__')
        and (
            _object.__name__.startswith(
                f'{FILL_CALLABLE_PREFIX}{FIXTURE_CALLABLE_INFIX}'
            )
            or _object.__name__.startswith(
                f'{FLUSH_CALLABLE_PREFIX}{FIXTURE_CALLABLE_INFIX}'
            )
        )
    )


def convert_path_to_module_name(path: str):
    """Convert file path to a module name - /app/fixtures.py -> app.fixtures"""
    return path.split('.py')[0].replace('/', '.')


def all_fixtures() -> Iterator[Fixture]:
    """Return all fixtures from all modules."""
    for file in fixture_files():
        if module_fixtures := fixture_callables(convert_path_to_module_name(str(file))):
            yield from (fixture for fixture in module_fixtures)


def get_fixture(prefix: FixturePrefix, name: str) -> Optional[Fixture]:
    """Return a fixture based on a callable name."""
    return next(
        (fixture for fixture in all_fixtures() if fixture.name == f'{prefix}{FIXTURE_CALLABLE_INFIX}{name}'), None,
    )


class Command(BaseCommand):
    help = 'Simple utility command to organize handling fixtures in Django'

    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)

        parser.add_argument(
            '--all',
            action='store_true',
            default=False,
            help='Show all available fixtures',
        )
        subparsers = parser.add_subparsers(dest='cmd')

        fill_parser = subparsers.add_parser('fill', help='Load fixtures with fill_ prefix')
        fill_parser.add_argument(
            'fixture_name', nargs='?', type=str, help='Fixture callable name with fill_ prefix that will be called'
        )

        flush_parser = subparsers.add_parser("flush", help='Load fixtures with flush_ prefix')
        flush_parser.add_argument(
            'fixture_name', nargs='?', type=str, help='Fixture callable name with flush_ prefix that will be called',
        )

    def handle(self, *args: Any, **options: Any) -> None:
        if options['all']:
            count = 0
            for fixture_obj in all_fixtures():
                self.stdout.write(f'./manage.py fixtures {str(fixture_obj)}\n')
                count += 1
            self.stdout.write(self.style.SUCCESS(f'✨ Found {count} fixture(s)'))
            return

        cmd = options.get('cmd')
        fixture_name = options.get('fixture_name')

        if not cmd:
            raise CommandError("Error: command must be specified. Choose from: 'fill' or 'flush'")

        if not fixture_name:
            raise CommandError(
                'Error: fixture name argument must be specified. '
                f"Show all available fixtures with '--all' option"
            )

        fixture = get_fixture(cmd, fixture_name)
        if not fixture:
            raise CommandError(
                f'Error: unrecognized fixture {fixture_name}. '
                f"Show all available fixtures with '--all' option"
            )

        self.stdout.write(
            self.style.WARNING(f'🤞 Loading {fixture.name} fixture...')
        )
        with transaction.atomic():
            fixture.callable()
        self.stdout.write(self.style.SUCCESS('🚀 Fixture loaded successfully'))
