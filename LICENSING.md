# Licensing

Copyright (c) 2026 Kevin Sullivan, for original Cairn project material.

## Fonts

The original Cairn and Cairn Mono font binaries in `desktop/` and `web/fonts/`,
and copies of those fonts embedded in HTML or CSS, are Font Software under
the SIL Open Font License 1.1 in [OFL.txt](OFL.txt).
**Cairn** and **Cairn Mono** are Reserved Font Names.

You may use and embed the fonts, including in commercial documents and apps,
under the OFL. Keep the copyright and license with redistributed fonts.
Modified versions need different primary font names unless the copyright
holder grants permission. The reservation does not prevent using the original
fonts by their existing names, and it does not license or reserve unrelated
uses of the ordinary word “cairn”. Read OFL.txt for the complete conditions.
Documents made with the fonts do not become OFL-licensed documents.

Each distributed font contains the copyright, reserved names, complete OFL
text, and license URL in its name table. This includes the older spacing
examples embedded in the comparison pages.

## Scripts, themes, and documentation

Kevin Sullivan's original Python, Swift, JavaScript, and Go scripts in `source/`
and the theme source directories, original theme CSS/configuration, and project
documentation are licensed under [MIT](LICENSE). This grant includes the
project's original drawing-source code; the generated font binaries are
distributed under the OFL as specified above.

An HTML or CSS file can contain both MIT-licensed project code and an
OFL-licensed embedded font. Its third-party content retains its own license.
The MIT grant does not replace the OFL or any third-party license.

## Third-party material

[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) identifies the Nord reference
stylesheet, Nord palette, their copyright holders, and preserved MIT notices.
These materials are not claimed as Kevin Sullivan's work.

Elbjorg was an early visual reference. The original Elbjorg font and inherited
ornament outlines are excluded from this distribution and from these grants.
The historical study files outside this repository are not licensed here.
The source painting used during palette exploration is also excluded.
Build dependencies are obtained separately under their own licenses.

## Rebuilding licensed packages

The font builders read OFL.txt for their metadata. After rebuilding fonts or
editing the package, run `python source/license_fonts.py` to synchronize the
distributed and embedded font metadata and package hashes. Run
`python source/check_licensing.py` to verify the license boundaries and notices.
Include OFL.txt when distributing a font; its full embedded license also
travels with standalone font specimens.
