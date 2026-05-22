#!/usr/bin/env python3
import argparse
import os
import re
import sys
from dotenv import load_dotenv
from notion_client import Client

load_dotenv(override=True)


def parse_page_id(value: str) -> str:
    """Extract raw UUID from a Notion URL or return the value as-is."""
    match = re.search(r"([a-f0-9]{32})", value.replace("-", ""))
    if match:
        raw = match.group(1)
        return f"{raw[:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:]}"
    return value


def list_children(notion, block_id):
    """Return all child blocks, handling pagination."""
    blocks = []
    cursor = None
    while True:
        kwargs = {"block_id": block_id}
        if cursor:
            kwargs["start_cursor"] = cursor
        try:
            resp = notion.blocks.children.list(**kwargs)
        except Exception as e:
            print(f"  [warn] Cannot list children of {block_id}: {e}", file=sys.stderr)
            break
        blocks.extend(resp.get("results", []))
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return blocks


def walk(notion, block_id, find, replace, dry_run, visited, changes):
    """Recursively walk all blocks under block_id, renaming matching child pages and databases."""
    if block_id in visited:
        return
    visited.add(block_id)

    for block in list_children(notion, block_id):
        btype = block["type"]
        bid = block["id"]
        has_children = block.get("has_children", False)

        if btype == "child_database":
            old_title = block["child_database"]["title"]
            if find in old_title:
                new_title = old_title.replace(find, replace)
                print(f"{'[dry-run] ' if dry_run else ''}Rename database: \"{old_title}\" → \"{new_title}\"")
                if not dry_run:
                    notion.databases.update(
                        bid,
                        title=[{"type": "text", "text": {"content": new_title}}],
                    )
                changes.append(("database", old_title, new_title))

        elif btype == "child_page":
            old_title = block["child_page"]["title"]
            if find in old_title:
                new_title = old_title.replace(find, replace)
                print(f"{'[dry-run] ' if dry_run else ''}Rename page: \"{old_title}\" → \"{new_title}\"")
                if not dry_run:
                    notion.pages.update(
                        bid,
                        properties={"title": {"title": [{"type": "text", "text": {"content": new_title}}]}},
                    )
                changes.append(("page", old_title, new_title))
            # Always recurse into child pages to find nested items
            if has_children:
                walk(notion, bid, find, replace, dry_run, visited, changes)

        elif has_children:
            # Container block (callout, toggle, column, synced_block, etc.)
            # Recurse to find nested child_page / child_database blocks
            walk(notion, bid, find, replace, dry_run, visited, changes)


def main():
    parser = argparse.ArgumentParser(
        description="Recursively rename Notion pages and databases under a parent page."
    )
    parser.add_argument("--page-id", required=True, help="Notion page ID or URL (root of the walk)")
    parser.add_argument("--find", required=True, help="String to find in titles")
    parser.add_argument("--replace", required=True, help="Replacement string")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying them")
    args = parser.parse_args()

    api_key = os.environ.get("NOTION_API_KEY")
    if not api_key:
        sys.exit("Error: NOTION_API_KEY not set. Add it to .env or set it in your environment.")

    notion = Client(auth=api_key)
    page_id = parse_page_id(args.page_id)

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Walking \"{page_id}\" — find \"{args.find}\" → replace \"{args.replace}\"\n")

    visited = set()
    changes = []
    walk(notion, page_id, args.find, args.replace, args.dry_run, visited, changes)

    print(f"\n{'─' * 60}")
    if changes:
        suffix = " (dry run — no changes applied)" if args.dry_run else ""
        print(f"{len(changes)} item(s) {'would be ' if args.dry_run else ''}renamed{suffix}.")
    else:
        print(f"No items with \"{args.find}\" in the title found.")


if __name__ == "__main__":
    main()
