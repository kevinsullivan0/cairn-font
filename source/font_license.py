"""Shared licensing metadata for Cairn builders. Script code: MIT."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OFL_TEXT = (ROOT / 'OFL.txt').read_text(encoding='utf-8').strip()
COPYRIGHT = OFL_TEXT.split('\n\n', 1)[0]
LICENSE_URL = 'https://openfontlicense.org'


def name_fields():
    return {'copyright': COPYRIGHT, 'licenseDescription': OFL_TEXT,
            'licenseInfoURL': LICENSE_URL}


def apply_metadata(font):
    """Set all existing name-table locales, including ones lacking a license URL."""
    locales = {(n.platformID, n.platEncID, n.langID) for n in font['name'].names}
    for platform, encoding, language in locales:
        for name_id, value in [(0, COPYRIGHT), (13, OFL_TEXT), (14, LICENSE_URL)]:
            font['name'].setName(value, name_id, platform, encoding, language)
