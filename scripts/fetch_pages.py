"""
Download all Moroccan Muhammadi mushaf pages from mushaf.ma.

Pages 3..640 (638 pages of main mushaf). Some higher page numbers (642+)
contain appendix material — handled separately.

Polite: ~1 req/sec, proper User-Agent, retries on failure.
"""
import io, os, sys, time, urllib.request, urllib.error, ssl

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'raw', 'muhammadi-pages')
OUT_DIR = os.path.abspath(OUT_DIR)
os.makedirs(OUT_DIR, exist_ok=True)

BASE = "https://mushaf.ma/fahres/page/images/muhammadi/page{}.png"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (data-foundation rebuild for Nur Al-Hifz Quran app; contact via project owner)',
    'Accept': 'image/png,image/*,*/*',
}

# Ignore SSL issues (server chain is fine but Windows may be picky)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

START = int(os.environ.get('START_PAGE', '3'))
END = int(os.environ.get('END_PAGE', '640'))

def fetch(page_num, retries=3):
    url = BASE.format(page_num)
    out_path = os.path.join(OUT_DIR, f'page{page_num:03d}.png')
    if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
        return 'skip', os.path.getsize(out_path)
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
                data = r.read()
                if len(data) < 1000:
                    return 'small', len(data)
                with open(out_path, 'wb') as f:
                    f.write(data)
                return 'ok', len(data)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return '404', 0
            if attempt == retries - 1:
                return f'http{e.code}', 0
        except Exception as e:
            if attempt == retries - 1:
                return f'err:{type(e).__name__}', 0
        time.sleep(2 ** attempt)
    return 'fail', 0

def main():
    total = 0
    ok = 0
    skipped = 0
    failed = []
    start_time = time.time()
    for p in range(START, END + 1):
        total += 1
        status, size = fetch(p)
        if status == 'ok':
            ok += 1
            print(f'  p{p:03d}  OK  ({size/1024:.0f} KB)')
        elif status == 'skip':
            skipped += 1
        elif status == '404':
            print(f'  p{p:03d}  404')
            failed.append((p, '404'))
        else:
            print(f'  p{p:03d}  FAIL: {status}')
            failed.append((p, status))
        # be polite: 0.4s between new downloads
        if status == 'ok':
            time.sleep(0.4)
    elapsed = time.time() - start_time
    print()
    print(f'Total : {total}')
    print(f'OK    : {ok}')
    print(f'Skip  : {skipped} (already downloaded)')
    print(f'Fail  : {len(failed)}')
    print(f'Time  : {elapsed:.1f}s')
    if failed:
        print('Failures:')
        for p, why in failed:
            print(f'  p{p:03d}  {why}')

if __name__ == '__main__':
    main()
