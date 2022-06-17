import argparse
import sys

from alembic.config import CommandLine

from market.db.utils import create_alembic_config
from market.config import settings


alembic = CommandLine()
alembic.parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
alembic.parser.add_argument('--db-url', default=settings.db_url)


def main():
    args = alembic.parser.parse_args()

    if 'cmd' not in args:
        print('You must specify the command', file=sys.stderr)
        exit(1)

    config = create_alembic_config(args.db_url)
    exit(alembic.run_cmd(config, args))


if __name__ == '__main__':
    main()
