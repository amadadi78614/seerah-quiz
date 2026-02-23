#!/usr/bin/env python3
"""
update.py — Seerah Quiz Master Update Script
=============================================
Drop new .xlsx files into the new-questions/ folder, then run:

    python3 scripts/update.py

This will:
  1. Parse all .xlsx files in new-questions/
  2. Deduplicate against existing questions in data/
  3. Update data/world*.json files
  4. Rebuild all HTML files
  5. Print a summary of what changed

After running, commit and push to GitHub — Vercel auto-deploys.
"""

import subprocess, sys, os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
SCRIPTS  = BASE_DIR / 'scripts'

def run(script, *args):
    cmd = [sys.executable, str(SCRIPTS / script)] + list(args)
    result = subprocess.run(cmd, cwd=str(BASE_DIR), capture_output=False)
    return result.returncode == 0

def main():
    print('=' * 50)
    print('  Seerah Quiz — Update Pipeline')
    print('=' * 50)

    # Check for new files
    new_files = list((BASE_DIR / 'new-questions').glob('*.xlsx')) + \
                list((BASE_DIR / 'new-questions').glob('*.xls'))
    if not new_files:
        print('\n  No .xlsx files found in new-questions/')
        print('  Drop your Excel files there and run again.')
        return

    print(f'\n  Found {len(new_files)} file(s) to process:')
    for f in new_files:
        print(f'    • {f.name}')

    print('\n[Step 1/2] Parsing & deduplicating questions...')
    if not run('parse_all.py', '--input-dir', str(BASE_DIR / 'new-questions')):
        print('ERROR: parse_all.py failed'); sys.exit(1)

    print('\n[Step 2/2] Rebuilding HTML files...')
    if not run('build_html.py'):
        print('ERROR: build_html.py failed'); sys.exit(1)

    print('\n' + '=' * 50)
    print('  ✓ Update complete!')
    print('  Next steps:')
    print('    git add .')
    print('    git commit -m "Add new questions"')
    print('    git push')
    print('  Vercel will auto-deploy within ~30 seconds.')
    print('=' * 50)

if __name__ == '__main__':
    main()
