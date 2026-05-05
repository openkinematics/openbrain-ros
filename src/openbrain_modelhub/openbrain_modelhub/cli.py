"""Console scripts: ``modelhub_pull`` and ``modelhub_list``."""

from __future__ import annotations

import argparse
import sys

from openbrain_modelhub.client import (
    DEFAULT_BASE_URL,
    DEFAULT_LOCAL_ROOT,
    ModelHubClient,
    iter_local_models,
)


def _client_from_args(args: argparse.Namespace) -> ModelHubClient:
    return ModelHubClient(base_url=args.base_url, local_root=args.local_root)


def pull(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="modelhub_pull")
    parser.add_argument("model_id")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--local-root", default=DEFAULT_LOCAL_ROOT, type=type(DEFAULT_LOCAL_ROOT))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    client = _client_from_args(args)
    target = client.pull(args.model_id, force=args.force)
    print(target)
    return 0


def ls(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="modelhub_list")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--local-root", default=DEFAULT_LOCAL_ROOT, type=type(DEFAULT_LOCAL_ROOT))
    parser.add_argument(
        "--remote",
        action="store_true",
        help="List models on the Hub instead of locally cached ones.",
    )
    args = parser.parse_args(argv)

    if args.remote:
        for meta in _client_from_args(args).list():
            print(f"{meta.id:>32}  {meta.version:>12}  {meta.framework:<14}  {meta.name}")
    else:
        for path in iter_local_models(args.local_root):
            print(path)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(pull(sys.argv[1:]))
