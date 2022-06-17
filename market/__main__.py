import argparse

import uvicorn

from market.config import settings


parser = argparse.ArgumentParser()
parser.add_argument('--app-host', default=settings.app_host)
parser.add_argument('--app-port', default=settings.app_port, type=int)


def main():
    args = parser.parse_args()
    uvicorn.run(
        'market.app:get_app',
        factory=True,
        host=args.app_host,
        port=args.app_port,
        reload=settings.is_debug
    )


if __name__ == '__main__':
    main()
