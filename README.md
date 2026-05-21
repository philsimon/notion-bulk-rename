# notion-bulk-rename

Rename child pages and databases on a Notion parent page via find/replace string substitution. Useful for batch-renaming prefixes, seasons, or any repeating title pattern across many pages at once.

## What It Does

Given a Notion parent page, `rh_rename.py` fetches all child pages and databases, finds any whose titles contain your search string, and replaces it with your replacement string. Run with `--dry-run` first to preview changes before applying them.

## Prerequisites

- Python 3.8 or later
- A [Notion internal integration](https://www.notion.so/my-integrations) with access to the target parent page

## Installation

```bash
git clone https://github.com/philsimon/notion-bulk-rename.git
cd notion-bulk-rename
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and paste in your Notion integration token:

```
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Make sure the integration has been connected to the target Notion page (open the page in Notion → ··· menu → Connections → add your integration).

## Usage

```bash
.venv/bin/python rh_rename.py \
  --page-id "https://www.notion.so/Your-Page-abc123..." \
  --find "Old Prefix" \
  --replace "New Prefix" \
  --dry-run
```

Remove `--dry-run` to apply changes.

### Flags

| Flag | Required | Description |
|---|---|---|
| `--page-id` | Yes | Full Notion URL or raw UUID of the parent page |
| `--find` | Yes | String to search for in child titles |
| `--replace` | Yes | Replacement string |
| `--dry-run` | No | Preview changes without applying them |

### Example Output

**Dry run:**
```
[dry-run] Renamed database: "Q1 Report" → "Q2 Report"
[dry-run] Renamed database: "Q1 Notes" → "Q2 Notes"
[dry-run] Renamed page: "Q1 Summary" → "Q2 Summary"

3 item(s) would be renamed (dry run — no changes applied).
```

**Live run:**
```
Renamed database: "Q1 Report" → "Q2 Report"
Renamed database: "Q1 Notes" → "Q2 Notes"
Renamed page: "Q1 Summary" → "Q2 Summary"

3 item(s) renamed.
```

## Notes

- Works on `child_database` and `child_page` block types.
- Handles up to ~100 children per page (Notion API single-call limit).
- Accepts full Notion URLs or raw UUIDs for `--page-id`.

## Claude Code Skill

If you use [Claude Code](https://claude.ai/code), copy `notion-bulk-rename.md` from this repo into `~/.claude/skills/`. Claude will then handle the workflow — asking for the parent page, find string, and replace string, running a dry-run preview, and applying changes on your confirmation.

## License

MIT
