import sqlite3
import json
import re

DB_FILE = 'recipes.db'


def normalize_instruction(step):
    if not isinstance(step, str):
        return step
    s = step.strip()
    # If looks like JSON array
    if s.startswith('[') and s.endswith(']'):
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                text = ' '.join([str(t).strip() for t in parsed if t])
                text = re.sub(r"\s+([.,;:!?])", r"\1", text)
                s = text
        except Exception:
            pass
    try:
        if '\\u' in s or '\\n' in s:
            s = s.encode('utf-8').decode('unicode_escape')
    except Exception:
        pass
    s = s.replace('â', '')
    s = s.replace('\u00b0', '')
    s = s.replace('Â', '')
    s = re.sub(r'[\x00-\x1f\x7f]', '', s)
    return s.strip()


def sample_and_print(limit=5):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('SELECT id, name, instructions FROM recipes WHERE instructions IS NOT NULL LIMIT ?', (limit,))
    rows = cur.fetchall()
    conn.close()

    for r in rows:
        rid, name, instr = r
        print('---')
        print('id:', rid)
        print('name:', name)
        print('raw instructions field:')
        print(instr[:1000])
        parts = [p.strip() for p in instr.split('|') if p.strip()]
        print('\nSplit into', len(parts), 'parts. Showing samples:')
        for i, p in enumerate(parts[:5]):
            print(f'  Part {i+1} RAW: {p[:300]}')
            print('  Part normalized:')
            print('    ', normalize_instruction(p)[:300])
        print('\n')

if __name__ == "__main__":
    sample_and_print(5)
