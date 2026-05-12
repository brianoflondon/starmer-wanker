#!/usr/bin/env python3
"""
Fetches MP names from the Google Sheet and looks up each one via the
UK Parliament Members API. Outputs parliament-data.json in the repo root.

Run locally or via GitHub Actions.
"""

import csv
import io
import json
import os
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

SHEET_CSV = (
    "https://docs.google.com/spreadsheets/d/"
    "1OBYlmRwHPlRa9Lsk6nTGlgX7Ixn1C3oX6v-f6ogZDEI/export?format=csv&gid=0"
)
PARLIAMENT_API = "https://members-api.parliament.uk/api/Members/Search"
OUTPUT_FILE = "parliament-data.json"
HONORIFICS = re.compile(r"^(Sir|Dame|Dr|Mr|Mrs|Ms|Miss)\s+", re.IGNORECASE)

PARLIAMENT_MEMBER_EXCEPTIONS = {
    "chris hinchcliff": {
        "id": 5244,
        "constituency": "North East Hertfordshire",
    },
    "catheine west": {
        "id": 4523,
        "constituency": "Hornsey and Friern Barnet",
    },
    "abitsam mohamed": {
        "id": 5142,
        "constituency": "Sheffield Central",
    },
    "antonia antoniazzi": {
        "id": 4623,
        "constituency": "Gower",
    },
    "rebecca long-bailey": {
        "id": 4396,
        "constituency": "Salford",
    },
}


def fetch_mp_names() -> list[str]:
    req = urllib.request.Request(SHEET_CSV, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        text = r.read().decode("utf-8")
    reader = csv.reader(io.StringIO(text))
    names = []
    for i, row in enumerate(reader):
        if i == 0 or not row:
            continue
        cell = ""
        if len(row) > 1 and row[1].strip():
            cell = row[1].strip()
        elif row[0].strip():
            cell = row[0].strip()
        if not cell:
            continue
        name = cell.split(",")[0].strip() if "," in cell else cell
        if name:
            names.append(name)
    return names


def lookup_mp(name: str) -> dict | None:
    name_lower = name.lower()
    if name_lower in PARLIAMENT_MEMBER_EXCEPTIONS:
        print(f"  ⟳ {name}: exception mapping used")
        return PARLIAMENT_MEMBER_EXCEPTIONS[name_lower]

    url = f"{PARLIAMENT_API}?Name={urllib.parse.quote(name)}&House=1&skip=0&take=5"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.load(r)
    except Exception as exc:
        print(f"  ✗ {name}: {exc}")
        return None

    items = data.get("items", [])
    if not items:
        print(f"  – {name}: no results")
        return None

    stripped = HONORIFICS.sub("", name_lower)

    match = next(
        (
            item
            for item in items
            if item["value"]["nameDisplayAs"].lower() == name_lower
            or item["value"]["nameListAs"].lower() == name_lower
            or HONORIFICS.sub("", item["value"]["nameDisplayAs"].lower()) == stripped
        ),
        items[0],  # fall back to first result
    )

    m = match["value"]
    constituency = (m.get("latestHouseMembership") or {}).get("membershipFrom", "")
    print(f"  ✓ {name} → {constituency} (id {m['id']})")
    return {"id": m["id"], "constituency": constituency}


def main() -> None:
    print("Fetching MP names from Google Sheet…")
    names = fetch_mp_names()
    print(f"Found {len(names)} MPs\n")

    members: dict[str, dict] = {}
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
            members.update(existing.get("members", {}))
            print(f"Loaded {len(members)} existing member entries from {OUTPUT_FILE}\n")
        except Exception as exc:
            print(f"Warning: failed to read {OUTPUT_FILE}: {exc}")

    for name in names:
        key = name.lower()
        existing_member = members.get(key)
        if existing_member and existing_member.get("id") and existing_member.get("constituency"):
            print(f"  → {name}: already cached, skipping")
            continue

        result = lookup_mp(name)
        if result:
            members[key] = result
        time.sleep(0.25)  # be polite to the API

    output = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "members": members,
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nWritten {OUTPUT_FILE} with {len(members)}/{len(names)} entries matched.")


if __name__ == "__main__":
    main()
