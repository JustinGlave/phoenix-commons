"""GitHub Releases auto-updater — API client.

Public API:
    UpdateInfo (dataclass)
    check_for_update(owner, repo, current_version, zip_asset_name)
        -> UpdateInfo | None

Ported and parameterized from
``Job Tracker/starter_package/updater.py:60-110``. The original used
module-level constants for ``GITHUB_OWNER``, ``GITHUB_REPO``,
``ZIP_ASSET_NAME``, ``EXE_NAME``; here those are function parameters so the
commons module serves every tool without baked-in production values.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 8  # seconds


@dataclass
class UpdateInfo:
    """Update metadata returned by :func:`check_for_update`."""
    current_version: str
    latest_version: str
    download_url: str
    release_notes: str


def _parse_version(tag: str) -> tuple[int, ...]:
    """Convert ``'v1.2.3'``, ``'V1.2.3'``, or ``'1.2.3'`` to ``(1, 2, 3)``
    for ordered comparison.

    Returns ``(0,)`` if the tag is empty or unparseable. Matches the
    starter_package behaviour so a malformed remote tag never suppresses
    valid local versions.
    """
    cleaned = tag.lstrip("vV").strip()
    try:
        return tuple(int(part) for part in cleaned.split("."))
    except ValueError:
        return (0,)


def check_for_update(
    owner: str,
    repo: str,
    current_version: str,
    zip_asset_name: str,
) -> Optional[UpdateInfo]:
    """Query the GitHub Releases API for ``<owner>/<repo>``.

    Returns an :class:`UpdateInfo` when ``zip_asset_name`` is attached to a
    release whose tag parses to a strictly newer version than
    ``current_version``. Returns ``None`` otherwise — including when the
    network is unavailable, GitHub returns garbled JSON, or no matching
    asset is attached.

    Safe to call from a background thread — never raises. Network errors are
    logged at ``DEBUG`` level; payload/parsing problems at ``WARNING``.
    """
    releases_api = (
        f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    )
    try:
        req = urllib.request.Request(
            releases_api,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": zip_asset_name,
            },
        )
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            data = json.loads(resp.read().decode())

        latest_tag = data.get("tag_name", "")
        if not latest_tag:
            return None
        if _parse_version(latest_tag) <= _parse_version(current_version):
            return None  # already up to date

        assets = data.get("assets", [])
        zip_asset = next(
            (
                a
                for a in assets
                if a.get("name", "").lower() == zip_asset_name.lower()
            ),
            None,
        )
        if zip_asset is None:
            logger.warning(
                "New release %s found but asset %s not attached.",
                latest_tag,
                zip_asset_name,
            )
            return None

        return UpdateInfo(
            current_version=current_version,
            latest_version=latest_tag.lstrip("vV"),
            download_url=zip_asset["browser_download_url"],
            release_notes=data.get("body", "").strip(),
        )

    except urllib.error.URLError as exc:
        logger.debug("Update check failed (network): %s", exc)
        return None
    except (json.JSONDecodeError, KeyError, TypeError, ValueError, AttributeError) as exc:
        logger.warning("Update check failed: %s", exc)
        return None
