"""Check the real Jekyll output without network requests or third-party dependencies."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path('_site').resolve()
BASE = '/pin-log'

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = []
        self.language = None
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'html':
            self.language = attrs.get('lang')
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        for key in ('href', 'src'):
            if attrs.get(key):
                self.links.append(attrs[key])

assert ROOT.is_dir(), 'Jekyll output is missing'
for path in (ROOT/'index.html', ROOT/'archive.html', ROOT/'tags.html', ROOT/'assets/css/notebook.css', ROOT/'assets/js/notebook.js'):
    assert path.is_file(), f'Missing output: {path}'
errors = []
for path in ROOT.rglob('*.html'):
    if path.name == 'FAQ.html':
        continue
    parser = Page()
    parser.feed(path.read_text())
    if parser.language != 'en':
        errors.append(f'{path.relative_to(ROOT)}: default language must be English')
    if len(parser.ids) != len(set(parser.ids)):
        errors.append(f'{path.relative_to(ROOT)}: duplicate IDs')
    for link in parser.links:
        url = urlsplit(link)
        if url.scheme or url.netloc or not url.path:
            continue
        target_path = unquote(url.path)
        if target_path.startswith(BASE + '/'):
            target = ROOT / target_path[len(BASE) + 1:]
        elif target_path == BASE:
            target = ROOT / 'index.html'
        elif target_path.startswith('/'):
            continue  # Links outside this project belong to the separate personal home.
        else:
            target = path.parent / target_path
        if not target.exists() and not target.with_suffix('.html').exists() and not (target/'index.html').exists():
            errors.append(f'{path.relative_to(ROOT)}: missing local target {link}')
assert not errors, '\n'.join(errors)
print('PASS: generated pages default to English; IDs and internal links are valid.')
