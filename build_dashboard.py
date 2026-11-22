"""Updates the ranked call list workbook and builds index.html from it.
Usage: python build_dashboard.py <ranked_call_list.xlsx> <flagged_accounts.csv> <out_dir>"""
import sys, json, subprocess, pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font
src_x, src_csv, out = sys.argv[1:4]
src = pd.read_csv(src_csv).set_index('account_id')
wb = load_workbook(src_x); ws = wb['call_list']
heads = [c.value for c in ws[1]]; assert heads[7] == 'rank'
ws['H1'] = 'overall_rank'
for c, h in zip('OPQ', ['status', 'domain_type', 'student_signups']):
    ws[f'{c}1'] = h; ws[f'{c}1']._style = ws['N1']._style
status = {'scored': 'Prospect', 'already_paid': 'Already paying'}
for n in range(2, ws.max_row + 1):
    aid, grp = ws[f'A{n}'].value, ws[f'E{n}'].value; s = src.loc[aid]
    st = status.get(grp) or ('School' if s.domain_type in ('university', 'k12_school') else 'Personal')
    ws[f'H{n}'] = n - 1                                    # sheet order = scored, paying, not scored
    ws[f'O{n}'], ws[f'P{n}'], ws[f'Q{n}'] = st, s.domain_type, int(s.student_signups)
    f = ws[f'G{n}'].value; ws[f'G{n}'] = f.replace('IF($E%d<>"scored","",' % n, 'IF($E%d<>"scored",0,' % n)
    ws[f'F{n}'] = f'=IF(G{n}>=80,"Call now",IF(G{n}>=50,"Call this week","Nurture"))'
    if st == 'School':
        k = int(s.student_signups); ws[f'I{n}'] = f"School workspace with {k} student sign-up{'s' if k != 1 else ''}; not a team buyer."
    for c in 'OPQ': ws[f'{c}{n}'].font = Font(name='Arial', size=10)
nt = wb['notes']
for r in range(1, nt.max_row + 1):
    a = nt.cell(r, 1).value or ''
    for old, new, pat in [('call_first (score 60+)', 'Call now (80-100)', 'Call now'), ('call_if_time (score 20-59)', 'Call this week (50-79)', 'Call this week'), ('dont_call (score under 20)', 'Nurture (0-49)', 'Nurture')]:
        if a == old: nt.cell(r, 1).value = new; nt.cell(r, 2).value = f'=COUNTIF(call_list!F:F,"{pat}")'
    if a in ('already_paid', 'not_scored') and r > 10 and 'F:F' in str(nt.cell(r, 2).value): nt.cell(r, 1).value = a + ' (band: Nurture, score 0)'; nt.cell(r, 2).value = f'=COUNTIF(call_list!E:E,"{a}")'
    if a.startswith('3. Bands'): nt.cell(r, 2).value = 'Call now = 80-100, Call this week = 50-79, Nurture = 0-49. Paying and school/personal accounts have score 0 and so show Nurture; status says why.'
    if a.startswith('4. Rank'): nt.cell(r, 2).value = 'overall_rank 1-1,200: scored accounts 1-606, then already-paying accounts, then school and personal accounts (by account_id). Written values; they do not update if usage is edited.'
wb.save(f'{out}/Q3_2026_ranked_call_list_updated.xlsx')
subprocess.run(['python3', '/mnt/skills/public/xlsx/scripts/recalc.py', f'{out}/Q3_2026_ranked_call_list_updated.xlsx', '120'], check=True)
x = pd.read_excel(f'{out}/Q3_2026_ranked_call_list_updated.xlsx', sheet_name='call_list')
rows = [dict(id=r.account_id, dom=r.company_domain, band=r.band, score=int(r.score), rank=int(r.overall_rank), reason=r.reason, status=r.status, dt=r.domain_type) for r in x.itertuples()]
html = open('template.html', encoding='utf-8').read().replace('__DATA__', json.dumps(rows, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'))
open(f'{out}/index.html', 'w', encoding='utf-8').write(html)
print(len(rows), 'rows embedded')
