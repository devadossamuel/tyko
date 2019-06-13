import argparse
import sys

from avforms.commands import commands


def setup_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="Extra", dest="subcommand")
    for k, v in commands.items():
        subparsers.add_parser(k, help=v[0])

    return parser


def main() -> None:
    parser = setup_cli_parser()
    args = parser.parse_args()

    if args.subcommand:
        commands[args.subcommand][1]()
        sys.exit()

    print("Running normal program")
