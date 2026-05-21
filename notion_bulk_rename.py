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


def main():
    parser = argparse.ArgumentParser(description="Rename Notion databases and pages on a parent page.")
    parser.add_argument("--page-id", required=True, help="Notion page ID or URL containing the databases/pages to rename")
    parser.add_argument("--find", required=True, help="String to find in child titles")
    parser.add_argument("--replace", required=True, help="Replacement string")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying them")
    args = parser.parse_args()

    api_key = os.environ.get("NOTION_API_KEY")
    if not api_key:
        sys.exit("Error: NOTION_API_KEY not set. Add it to .env or set it in your environment.")

    notion = Client(auth=api_key)
    page_id = parse_page_id(args.page_id)

    response = notion.blocks.children.list(block_id=page_id)
    blocks = response.get("results", [])

    if not blocks:
        print("No children found on this page.")
        return

    changes = 0

    for block in blocks:
        block_type = block.get("type")

        if block_type == "child_database":
            old_title = block["child_database"]["title"]
            if args.find in old_title:
                new_title = old_title.replace(args.find, args.replace)
                print(f"{'[dry-run] ' if args.dry_run else ''}Renamed database: \"{old_title}\" → \"{new_title}\"")
                if not args.dry_run:
                    notion.databases.update(
                        block["id"],
                        title=[{"type": "text", "text": {"content": new_title}}],
                    )
                changes += 1

        elif block_type == "child_page":
            old_title = block["child_page"]["title"]
            if args.find in old_title:
                new_title = old_title.replace(args.find, args.replace)
                print(f"{'[dry-run] ' if args.dry_run else ''}Renamed page: \"{old_title}\" → \"{new_title}\"")
                if not args.dry_run:
                    notion.pages.update(
                        block["id"],
                        properties={"title": {"title": [{"type": "text", "text": {"content": new_title}}]}},
                    )
                changes += 1

    if changes == 0:
        print(f"No children with \"{args.find}\" in the title found.")
    else:
        suffix = " (dry run — no changes applied)" if args.dry_run else ""
        print(f"\n{changes} item(s) {'would be ' if args.dry_run else ''}renamed{suffix}.")


if __name__ == "__main__":
    main()
