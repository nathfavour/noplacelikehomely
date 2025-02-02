#!/usr/bin/env python3
"""
noplacelikehomely CLI entry point.

This script starts the communications server that enables local network sharing of
files, clipboard data, etc.
"""

import argparse
import logging
import sys

from noplacelikehomely import __version__
from noplacelikehomely.config import update_config  # New import

__author__ = "nathfavour"
__copyright__ = "nathfavour"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description="Start noplacelike communications server"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host address (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port number (default: 8000)",
    )
    parser.add_argument(
        "-v", "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const", const=logging.INFO
    )
    parser.add_argument(
        "-vv", "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const", const=logging.DEBUG
    )
    # New CLI options to override config
    parser.add_argument("--upload-folder", type=str,
                        help="Folder path for uploads (overrides config)")
    parser.add_argument("--download-folder", type=str,
                        help="Folder path for downloads (overrides config)")
    # Set default loglevel if not specified
    parser.set_defaults(loglevel=logging.WARNING)
    return parser.parse_args(args)

def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )

def start_server(host, port):
    """Start the communications server using the robust server module."""
    from noplacelikehomely.server.server import run_server
    run_server(host, port)

def main(args):
    """Wrapper allowing :func:`start_server` to be called with string arguments in a CLI fashion

    Instead of returning the value from :func:`start_server`, it prints the result to the
    ``stdout`` in a nicely formatted message.

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--verbose", "42"]``).
    """
    args = parse_args(args)
    # Update config if user provides folder overrides
    overrides = {}
    if args.upload_folder:
        overrides["upload_folder"] = args.upload_folder
    if args.download_folder:
        overrides["download_folder"] = args.download_folder
    if overrides:
        update_config(**overrides)
    setup_logging(args.loglevel)
    _logger.debug("Initializing noplacelike server...")
    start_server(args.host, args.port)

def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])

if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html

    # After installing your project with pip, users can also run your Python
    # modules as scripts via the ``-m`` flag, as defined in PEP 338::
    #
    #     python -m noplacelikehomely.skeleton 42
    #
    run()
