"""Check distributed font licenses and third-party notices. Script code: MIT."""
from pathlib import Path
from io import BytesIO
import argparse
import base64
import hashlib
import html
import json

from fontTools.ttLib import TTFont
from font_license import OFL_TEXT, COPYRIGHT, LICENSE_URL
from license_fonts import FONT_DATA, NORD_FRAME


def font_copies(root):
    for folder, pattern in [('desktop', '*.ttf'), ('web/fonts', '*.woff')]:
        for path in sorted((root / folder).glob(pattern)):
            yield str(path.relative_to(root)), path.read_bytes()
    for path in sorted(root.rglob('*')):
        if path.suffix in {'.html', '.css'}:
            for i, match in enumerate(FONT_DATA.finditer(path.read_text())):
                yield f'{path.relative_to(root)}:embedded:{i}', base64.b64decode(match[2], validate=True)


def signature(data):
    font = TTFont(BytesIO(data), recalcBBoxes=False, recalcTimestamp=False)
    tables = {tag: font.getTableData(tag) for tag in font.keys()
              if tag not in {'GlyphOrder', 'name', 'head'}}
    tables['head-properties'] = {k: v for k, v in vars(font['head']).items()
                                 if k != 'checkSumAdjustment'}
    tables['other-names'] = {(n.nameID, n.platformID, n.platEncID, n.langID): n.toUnicode()
                            for n in font['name'].names if n.nameID not in {0, 13, 14}}
    return tables


def check(root, baseline=None):
    assert 'with Reserved Font Names "Cairn" and "Cairn Mono".' in OFL_TEXT
    assert (root / 'OFL.txt').read_text().strip() == OFL_TEXT
    copies = dict(font_copies(root))
    expected = {0: COPYRIGHT, 13: OFL_TEXT, 14: LICENSE_URL}
    for label, data in copies.items():
        font = TTFont(BytesIO(data), checkChecksums=2)
        assert font['name'].getDebugName(1) in {'Cairn', 'Cairn Mono'}, label
        for name_id, value in expected.items():
            names = [n.toUnicode() for n in font['name'].names if n.nameID == name_id]
            assert names and set(names) == {value}, (label, name_id)
        assert font['OS/2'].fsType == 0, label
        assert not any(0xE000 <= cp <= 0xF8FF for cp in font.getBestCmap()), label
    loose = [label for label in copies if ':embedded:' not in label]
    assert len(loose) == 16
    for path in sorted((root / 'desktop').glob('*.ttf')):
        ttf = TTFont(path)
        woff = TTFont(root / 'web/fonts' / (path.stem + '.woff'))
        assert set(ttf.keys()) == set(woff.keys())
        for tag in ttf.keys():
            if tag not in {'GlyphOrder', 'head'}:
                assert ttf.getTableData(tag) == woff.getTableData(tag), (path.name, tag)
    notice = (root / 'third-party/obsidian-nord-LICENSE.txt').read_text().strip()
    assert 'Copyright (c) 2020 Eric Davis' in notice
    assert 'The above copyright notice and this permission notice' in notice
    text = (root / 'themes/Cairn-Ash/compare-nord.html').read_text()
    frame = html.unescape(NORD_FRAME.search(text)[2])
    comment = ('\n/* Obsidian Nord reference stylesheet only.\n'
               + 'Source: https://github.com/insanum/obsidian_nord\n'
               + notice + '\n*/\n')
    assert comment in frame
    assert 'Copyright (c) 2016-present Sven Greb' in (root / 'third-party/nord-LICENSE.txt').read_text()
    assert not list(root.rglob('*Elbjorg*.ttf'))
    assert not list(root.rglob('*Elbjorg*.woff'))
    if baseline:
        previous = dict(font_copies(baseline))
        assert previous.keys() == copies.keys(), 'Font set changed'
        for label, data in copies.items():
            assert signature(data) == signature(previous[label]), ('Font design changed', label)
        old_frame = html.unescape(NORD_FRAME.search(
            (baseline / 'themes/Cairn-Ash/compare-nord.html').read_text())[2])
        # Compare the whole pane, allowing only this notice and licensed font payloads.
        strip_fonts = lambda value: FONT_DATA.sub('FONT_PAYLOAD', value)
        assert strip_fonts(old_frame) == strip_fonts(frame.replace(comment, '', 1)), 'Nord pane changed'
    manifests = 0
    for path in root.rglob('manifest.json'):
        manifest = json.loads(path.read_text())
        if 'files' not in manifest:
            continue
        manifests += 1
        for entry in manifest['files']:
            actual = hashlib.sha256((path.parent / entry['path']).read_bytes()).hexdigest()
            assert actual == entry['sha256'], (str(path.relative_to(root)), entry['path'])
    return {'status': 'passed', 'font_files': len(loose),
            'embedded_font_copies': len(copies) - len(loose),
            'metadata': 'All copyright, full OFL/RFN text, URL and embedding flags checked',
            'ttf_woff_roundtrips': 8, 'nord_notice': 'retained', 'hash_manifests': manifests,
            'baseline_comparison': 'All non-license tables, other names, and Nord pane unchanged' if baseline else 'not requested',
            'scope': 'Licensing and binary/table consistency; not a legal originality opinion or browser rendering test'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path, nargs='?', default=Path(__file__).resolve().parent.parent)
    parser.add_argument('--baseline', type=Path)
    args = parser.parse_args()
    print(json.dumps(check(args.root, args.baseline), indent=2))
