#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Add a command-line argument for the environment
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--env', type=str, default='local', help='The environment to run the application in')
    args, remaining_argv = parser.parse_known_args()

    # Set the DJANGO_ENV environment variable
    os.environ['DJANGO_ENV'] = args.env

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server_mgmt.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line([sys.argv[0]] + remaining_argv)


if __name__ == '__main__':
    main()
