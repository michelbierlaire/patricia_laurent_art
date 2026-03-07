from __future__ import annotations

import argparse

from patricia_laurent_art.site_generator import SiteGenerator
from patricia_laurent_art.settings import DEFAULT_BASE_URL, THEMES


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Generate the Patricia Laurent bilingual static website.')
    parser.add_argument('--base-url', default=DEFAULT_BASE_URL, help='Public base URL used for QR codes.')
    parser.add_argument('--theme', choices=sorted(THEMES), default=None, help='Optional theme override.')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    docs_dir = SiteGenerator().generate(base_url=args.base_url, theme=args.theme)
    print(f'Site generated in {docs_dir}')


if __name__ == '__main__':
    main()
