"""Rebuilds the call list dashboard when a new ranked call list comes in.

Usage:  python build_dashboard.py <ranked_call_list.xlsx> <flagged_accounts.csv> <out_dir>
Needs:  pandas and openpyxl (pip install pandas openpyxl), and template.html next to this script.
Writes: <out_dir>/index.html and <out_dir>/Q3_2026_ranked_call_list_updated.xlsx
"""
import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font

def find_soffice():
    for name in ('soffice', 'libreoffice'):
        if shutil.which(name): return shutil.which(name)
    for p in (r'C:\Program Files\LibreOffice\program\soffice.exe', r'C:\Program Files (x86)\LibreOffice\program\soffice.exe',
              '/Applications/LibreOffice.app/Contents/MacOS/soffice'):
        if os.path.exists(p): return p

def recalc(path):
    """Optional: fills in the formula results so other tools can read them. Needs LibreOffice."""
    exe = find_soffice()
    if not exe:
        print('LibreOffice not found: skipped recalculation. Excel and Google Sheets calculate the formulas when you open the file.')
        return
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([exe, '--headless', '--convert-to', 'xlsx', '--outdir', tmp, str(path)], check=True, capture_output=True)
        shutil.move(os.path.join(tmp, Path(path).name), path)
    print('Recalculated formulas with LibreOffice.')

def main(src_x, src_csv, out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    flags = pd.read_csv(src_csv).set_index('account_id')
    x = pd.read_excel(src_x, sheet_name='call_list')
    if list(x.columns)[:9] != ['account_id', 'company_domain', 'industry', 'rep_owner', 'group', 'band', 'score', 'rank', 'reason']:
        sys.exit('The call_list tab must be the original ranked call list (columns account_id ... reason, with a rank column).')
    order = x.group.map({'scored': 0, 'already_paid': 1, 'not_scored': 2})
    if order.isna().any() or not order.is_monotonic_increasing:
        sys.exit('Rows must be ordered: scored, then already_paid, then not_scored.')
    wb = load_workbook(src_x); ws = wb['call_list']
    ws['H1'] = 'overall_rank'
    for c, h in zip('OPQ', ['status', 'domain_type', 'student_signups']):
        ws[f'{c}1'] = h; ws[f'{c}1']._style = ws['N1']._style
    rows = []
    for i, r in enumerate(x.itertuples(), start=1):
        n = i + 1; f = flags.loc[r.account_id]
        status = {'scored': 'Prospect', 'already_paid': 'Already paying'}.get(r.group) or ('School' if f.domain_type in ('university', 'k12_school') else 'Personal')
        score = int(r.score) if r.group == 'scored' else 0
        band = 'Call now' if score >= 80 else 'Call this week' if score >= 50 else 'Nurture'
        reason = r.reason
        if status == 'School':
            k = int(f.student_signups); reason = f"School workspace with {k} student sign-up{'s' if k != 1 else ''}; not a team buyer."
        ws[f'H{n}'], ws[f'I{n}'] = i, reason
        ws[f'O{n}'], ws[f'P{n}'], ws[f'Q{n}'] = status, f.domain_type, int(f.student_signups)
        ws[f'G{n}'] = ws[f'G{n}'].value.replace(f'IF($E{n}<>"scored","",', f'IF($E{n}<>"scored",0,')
        ws[f'F{n}'] = f'=IF(G{n}>=80,"Call now",IF(G{n}>=50,"Call this week","Nurture"))'
        for c in 'OPQ': ws[f'{c}{n}'].font = Font(name='Arial', size=10)
        rows.append(dict(id=r.account_id, dom=r.company_domain, band=band, score=score, rank=i, reason=reason, status=status, dt=f.domain_type))
    if len(rows) != 1200 or len({r['id'] for r in rows}) != 1200:
        sys.exit('The page text says 1,200 accounts; this list has %d rows. Update template.html if the list size changed.' % len(rows))
    nt = wb['notes']
    for r in range(1, nt.max_row + 1):
        a = nt.cell(r, 1).value or ''
        for old, new, pat in [('call_first (score 60+)', 'Call now (80-100)', 'Call now'), ('call_if_time (score 20-59)', 'Call this week (50-79)', 'Call this week'), ('dont_call (score under 20)', 'Nurture (0-49)', 'Nurture')]:
            if a == old: nt.cell(r, 1).value = new; nt.cell(r, 2).value = f'=COUNTIF(call_list!F:F,"{pat}")'
        if a in ('already_paid', 'not_scored') and r > 10 and 'F:F' in str(nt.cell(r, 2).value):
            nt.cell(r, 1).value = a + ' (band: Nurture, score 0)'; nt.cell(r, 2).value = f'=COUNTIF(call_list!E:E,"{a}")'
        if a.startswith('3. Bands'): nt.cell(r, 2).value = 'Call now = 80-100, Call this week = 50-79, Nurture = 0-49. Paying and school/personal accounts have score 0 and so show Nurture; status says why.'
        if a.startswith('4. Rank'): nt.cell(r, 2).value = 'overall_rank 1-1,200: scored accounts first, then already-paying accounts, then school and personal accounts (by account_id). Written values; they do not update if usage is edited.'
    xlsx_out = out / 'Q3_2026_ranked_call_list_updated.xlsx'
    wb.save(xlsx_out); recalc(xlsx_out)
    html = (Path(__file__).parent / 'template.html').read_text(encoding='utf-8')
    data = json.dumps(rows, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    (out / 'index.html').write_text(html.replace('__DATA__', data), encoding='utf-8')
    print(len(rows), 'rows embedded. Wrote', out / 'index.html', 'and', xlsx_out)

if __name__ == '__main__':
    if len(sys.argv) != 4: sys.exit(__doc__)
    main(*sys.argv[1:4])
