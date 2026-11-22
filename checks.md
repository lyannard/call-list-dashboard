# Dashboard check report

Checks run on `index.html` and `Q3_2026_ranked_call_list_updated.xlsx` (tab `call_list`) on 2026-11-22. The page's own lookup code was run in Node against the data embedded in the page, and each answer was compared with the row in the sheet. Sheet row = overall_rank + 1 (row 1 is the header).

## The 10 rep lookups

| # | Lookup entered | Page shows | Sheet row | Result |
|---|---|---|---|---|
| 1 | ACC-10001 | rank 1086, score 0, Nurture / Personal | row 1087: rank 1086, score 0, Nurture | **PASS** |
| 2 | ACC-10587 | rank 417, score 7, Nurture / Prospect | row 418: rank 417, score 7, Nurture | **PASS** |
| 3 | ACC-11200 | rank 1200, score 0, Nurture / Personal | row 1201: rank 1200, score 0, Nurture | **PASS** |
| 4 | ` ACC-10342` (leading space) | rank 919, score 0, Nurture / Personal | row 920: rank 919, score 0, Nurture | **PASS** |
| 5 | `acc-10918` (lower case) | rank 680, score 0, Nurture / School | row 681: rank 680, score 0, Nurture | **PASS** |
| 6 | ACC-11347 | Message: "ACC-11347 is not in this call list." | No such row (IDs end at ACC-11200) | **PASS** |
| 7 | Picks `ACC-10587 · brightpath2587.com` from the list | rank 417, score 7, Nurture / Prospect (same as typing the ID) | row 418: rank 417, score 7, Nurture | **PASS** |
| 8 | Top school account | ACC-10575: rank 667, score 0, Nurture / School | row 668: rank 667, score 0, Nurture | **PASS** |
| 9 | Call now only | 16 accounts, ranks 1 to 16, in rank order | 16 Call now rows, rows 2 to 17 | **PASS** |
| 10 | ACC-10070 (paying) | rank 607, score 0, Nurture / Already paying + Already a customer badge | row 608: rank 607, score 0, Nurture | **PASS** |

Lookups passed: 10 of 10.

## All 1,200 IDs

| Check | Result |
|---|---|
| Every one of the 1,200 IDs returns an answer with rank, score, band and reason (including ACC-10001 and ACC-11200) | **PASS** |
| Data embedded in the page equals the workbook row for row (ID, domain, band, score, rank, reason, status, domain type) | **PASS** |
| Ranks run 1 to 1,200 with no gaps or repeats; no blank reason or score on any row | **PASS** |
| Picker: all 1,200 list labels (`ID · domain`) map back to their own account | **PASS** |
| Account IDs match the flagged accounts file; ACC-11347 is not in the list | **PASS** |

## Notes

- With the demo's band cut-offs, Call now has 16 accounts, Call this week has 1 and Nurture has 1,183. Paying, school and personal accounts have score 0, so they show Nurture; the status column says why.
- Lookup 7 was first marked FAIL by my own test, which looked for the picker text in the HTML file. The page builds that list when it loads, so the test was wrong, not the page. I re-tested by building every label the way the page does and mapping it back to its account.
- These checks read the data and run the lookup code. They do not test how the page looks in a browser.
