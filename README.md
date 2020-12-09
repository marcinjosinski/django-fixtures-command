# django-fixtures-command

[![Actions Status](https://github.com/marcinjosinski/django-fixtures-command/workflows/CI/badge.svg)](https://github.com/marcinjosinski/django-fixtures-command/actions)

Simple Django command that helps to organize your fixtures.


<p align="center">
  <img src="https://github.com/marcinjosinski/django-fixtures-command/blob/main/img/example.png" alt="Example usage of django-fixtures-command " width="738">
</p>


## Usage

Add `fixtures.py` files anywhere you want in your Django project. Put there the functions that handle fake data for development purposes.
The function must have `fill_` or `flush_` prefix and must be defined in the `fixtures.py` file to be found by `./manage.py fixtures` command.

## Commands

Display all available fixtures along with their docstrings:
```./manage.py fixtures --all```

Fill the database with fake data:
```./manage.py fixtures fill <fixture_name>```

Flush data from the database:
```./manage.py fixtures flush <fixture_name>```


## Example
It is convenient to use some tool to generate fake data for fixtures like the `factory_boy` library.

```py
def fill_profiles():
    """Fill the database with fake user profiles."""
    inactive_profile = ProfileFactory.create(
      user__password=EXAMPLE_PASSWORD, user__is_active=False,
    )
    active_profile = ProfileFactory.create(user__password=EXAMPLE_PASSWORD, user__is_active=True)
    admin_profile = ProfileFactory.create(
      user__password=EXAMPLE_PASSWORD, user__is_superuser=True, user__is_staff=True,
    )
    print('Inactive profile:', inactive_profile.user.email, 'password:', EXAMPLE_PASSWORD)
    print('Active profile:', active_profile.user.email, 'password:', EXAMPLE_PASSWORD)
    print('Admin profile:', admin_profile.user.email, 'password:', EXAMPLE_PASSWORD)


def flush_profiles():
    """Remove all user profiles."""
    Profile.objects.all().delete()
```

## Installation

Install with pip:

`python -m pip install django-fixtures-command`


Then add to your installed apps:
```py
INSTALLED_APPS = [
  ...,
  'django_fixtures_command'
]
```
