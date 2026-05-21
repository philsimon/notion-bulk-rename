---
name: notion-bulk-rename
description: Use when the user wants to rename child pages or databases on a Notion parent page by replacing a string in their titles.
---

# Notion Bulk Rename

Renames child databases and pages on a Notion parent page via find/replace string substitution.

## Script Location

The script lives wherever you cloned the repo. Set `SCRIPT_DIR` to that path:

```
SCRIPT_DIR=/path/to/notion-bulk-rename
```

The `.env` file in that directory must contain your `NOTION_API_KEY`.

## Required Inputs

Parse from the user's natural language prompt:

- **Page** — Notion page URL or raw UUID (the parent containing the items to rename)

Then ask the user these two questions in order:

1. "What string currently exists in the titles?"
2. "What string do you want to replace it with?"

Use the answers as `--find` and `--replace` respectively.

## Workflow

Always run dry-run first, show output, then ask the user to confirm before applying changes.

**Step 1 — Ask the two questions above and collect answers.**

**Step 2 — Dry run:**
```bash
cd /path/to/notion-bulk-rename && .venv/bin/python notion_bulk_rename.py \
  --page-id "PAGE_ID_OR_URL" \
  --find "FIND_STRING" \
  --replace "REPLACE_STRING" \
  --dry-run
```

**Step 3 — Show output and ask the user to confirm.**

**Step 4 — Live run:**
```bash
cd /path/to/notion-bulk-rename && .venv/bin/python notion_bulk_rename.py \
  --page-id "PAGE_ID_OR_URL" \
  --find "FIND_STRING" \
  --replace "REPLACE_STRING"
```

## Notes

- `--page-id` accepts full Notion URLs or raw UUIDs.
- Handles both `child_database` and `child_page` block types.
- Works up to ~100 children per page (Notion API single-call limit).
- Uses `load_dotenv(override=True)` — the `.env` value always wins over any shell environment variable.
