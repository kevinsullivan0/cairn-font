"""Refresh license metadata without changing font drawings, metrics, or features.

Script code: MIT. Generated font payloads: SIL OFL 1.1; see ../LICENSING.md.
Run after builders/package generators to update frozen embedded specimens too.
"""
from pathlib import Path
from io import BytesIO
import argparse
import base64
import hashlib
import html
import json
import re

from fontTools.ttLib import TTFont
from font_license import apply_metadata

FONT_DATA = re.compile(r'(data:font/(?:woff|ttf);base64,)([A-Za-z0-9+/=]+)')
NORD_FRAME = re.compile(r'(<iframe\b[^>]*\bid="frame-nord"[^>]*\bsrcdoc=")([^"]*)(")')


def update_fonts(root):
    cache = {}

    def licensed(data):
        if data in cache:
            return cache[data]
        font = TTFont(BytesIO(data), recalcBBoxes=False, recalcTimestamp=False)
        family = font['name'].getDebugName(1)
        if family not in {'Cairn', 'Cairn Mono'}:
            raise ValueError(f'Refusing to license unrecognized font: {family}')
        before = {t: font.getTableData(t) for t in font.keys()
                  if t not in {'GlyphOrder', 'name', 'head'}}
        head = {k: v for k, v in vars(font['head']).items() if k != 'checkSumAdjustment'}
        apply_metadata(font)
        output = BytesIO()
        font.save(output, reorderTables=False)
        result = output.getvalue()
        checked = TTFont(BytesIO(result), recalcBBoxes=False, recalcTimestamp=False)
        assert before == {t: checked.getTableData(t) for t in checked.keys()
                          if t not in {'GlyphOrder', 'name', 'head'}}, 'Non-license table changed'
        assert head == {k: v for k, v in vars(checked['head']).items()
                        if k != 'checkSumAdjustment'}, 'Font header properties changed'
        cache[data] = result
        return result

    loose = 0
    for folder, suffix in [('desktop', '*.ttf'), ('web/fonts', '*.woff')]:
        for path in sorted((root / folder).glob(suffix)):
            path.write_bytes(licensed(path.read_bytes()))
            loose += 1
    embedded = 0
    for path in sorted(root.rglob('*')):
        if path.suffix not in {'.html', '.css'}:
            continue
        text = path.read_text(encoding='utf-8')

        def replace(match):
            nonlocal embedded
            embedded += 1
            data = licensed(base64.b64decode(match[2], validate=True))
            return match[1] + base64.b64encode(data).decode('ascii')

        updated = FONT_DATA.sub(replace, text)
        if updated != text:
            path.write_text(updated, encoding='utf-8')
    return loose, embedded


def retain_nord_notice(root):
    path = root / 'themes/Cairn-Ash/compare-nord.html'
    text = path.read_text(encoding='utf-8')
    match = NORD_FRAME.search(text)
    if not match:
        raise ValueError('Nord reference iframe missing')
    frame = html.unescape(match[2])
    notice = (root / 'third-party/obsidian-nord-LICENSE.txt').read_text().strip()
    if notice not in frame:
        # Insert immediately before the original Nord CSS, leaving its bytes intact.
        start = frame.index('\n:root\n{\n    --dark0_x:')
        frame = (frame[:start] + '\n/* Obsidian Nord reference stylesheet only.\n'
                 + 'Source: https://github.com/insanum/obsidian_nord\n'
                 + notice + '\n*/\n' + frame[start:])
        text = text[:match.start(2)] + html.escape(frame, quote=True) + text[match.end(2):]
        path.write_text(text, encoding='utf-8')


def refresh_hashes(root):
    for filename in ['build-report.json', 'mono-build-report.json', 'validation.json']:
        path = root / filename
        report = json.loads(path.read_text())
        entries = report if isinstance(report, list) else report['styles']
        for entry in entries:
            family = 'CairnMono' if filename.startswith('mono-') else 'Cairn'
            stem = f"{family}-{entry['style'].replace(' ', '')}"
            ttf = root / 'desktop' / (stem + '.ttf')
            woff = root / 'web/fonts' / (stem + '.woff')
            entry['sha256'] = hashlib.sha256(ttf.read_bytes()).hexdigest()
            if 'ttf_bytes' in entry:
                entry['ttf_bytes'] = ttf.stat().st_size
                entry['woff_bytes'] = woff.stat().st_size
        path.write_text(json.dumps(report, indent=2) + '\n')
    # Theme bundles have their own hash manifests; update children before parents.
    for path in sorted(root.rglob('manifest.json'), key=lambda p: len(p.parts), reverse=True):
        manifest = json.loads(path.read_text())
        if 'files' not in manifest:
            continue  # Obsidian plugin/theme metadata, not a hash manifest.
        paths = {e['path'] for e in manifest['files']}
        if path == root / 'manifest.json':
            paths.update(['LICENSE', 'OFL.txt', 'LICENSING.md', 'THIRD_PARTY_NOTICES.md',
                          'third-party/nord-LICENSE.txt', 'third-party/obsidian-nord-LICENSE.txt',
                          'source/font_license.py', 'source/license_fonts.py', 'source/check_licensing.py'])
        manifest['files'] = [{'path': name,
                              'sha256': hashlib.sha256((path.parent / name).read_bytes()).hexdigest()}
                             for name in sorted(paths)]
        path.write_text(json.dumps(manifest, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path, nargs='?', default=Path(__file__).resolve().parent.parent)
    root = parser.parse_args().root
    loose, embedded = update_fonts(root)
    retain_nord_notice(root)
    refresh_hashes(root)
    print(json.dumps({'font_files': loose, 'embedded_font_copies': embedded,
                      'preserved': 'All non-license tables and header properties except checksum adjustment'}))


if __name__ == '__main__':
    main()
