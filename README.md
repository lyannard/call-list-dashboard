# Call List Dashboard

A single-file web page where a sales rep types or picks an account ID and sees its rank (of 1,200), score, call band, status and a one-line reason to open the call. Every number on the page is read from the ranked call list workbook, never typed in.

Open `index.html` in any browser. Nothing else is needed. See `checks.md` for the test results.

## Rebuilding when a new call list comes in

### What the script needs

1. **The ranked call list workbook** (`.xlsx`) with a `call_list` tab in the original layout: columns `account_id` through `reason` (including `rank`), rows ordered scored, then already_paid, then not_scored.
2. **The flagged accounts CSV**, which supplies `domain_type` and `student_signups` for each account.
3. **An output folder** for the two files the script writes. It is created if it does not exist.

`template.html` must sit next to `build_dashboard.py`. You also need Python 3.9 or newer.

### Steps

1. Install the two packages (one time):
   ```
   pip install pandas openpyxl
   ```
2. Run the script from the repo folder, using your own file paths:
   ```
   python build_dashboard.py "C:\path\to\ranked_call_list.xlsx" "C:\path\to\flagged_accounts.csv" output
   ```
3. Open `output/index.html` and look up a few accounts.

### What you get

- `output/index.html`: the dashboard with all rows embedded.
- `output/Q3_2026_ranked_call_list_updated.xlsx`: the workbook with `overall_rank` (1 to 1,200), `status`, `domain_type` and `student_signups` added, and the demo bands applied. Re-import it into the Google Sheet so the sheet and the page match.

### Good to know

- **LibreOffice is optional.** The script no longer needs a fixed path. If LibreOffice is installed (it looks on your PATH and in the usual Windows and Mac locations), the script also fills in the formula results. If not, it says so and carries on, and Excel or Google Sheets calculate the formulas when you open the file.
- **The page says 1,200 accounts.** If a new list has a different number of rows, the script stops and tells you. Update the text in `template.html` first.
- **Bands:** Call now is 80 to 100, Call this week is 50 to 79 and Nurture is 0 to 49. Paying, school and personal accounts have score 0, so they show Nurture; the status column says why.
- **If it stops with a message about columns or row order,** the workbook is not the original ranked list. Use the one exported before this script was run.
