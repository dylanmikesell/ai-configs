r"""Dump every branding fact needed to rebuild references/layouts.md from a .pptx.

Run this FIRST whenever the corporate template changes (see ../REBUILD.md). It reads
the raw OOXML with the standard library only (no python-pptx needed), so it works on
any .pptx and never depends on the thing it's inspecting.

    python scripts/inspect_template.py                 # inspects the bundled template
    python scripts/inspect_template.py path\to\new.pptx  # inspects a specific file

Prints JSON: slide size, theme fonts, theme colour scheme, company, and every layout
with its exact name (quirks like leading spaces preserved) and placeholder idx/type.
Hand the JSON to Claude and say "regenerate layouts.md for the new template".
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

DEFAULT = Path(__file__).resolve().parent.parent / "assets" / "ngi-template.pptx"
PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT

NS = {
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}
EMU_PER_IN = 914400
EMU_PER_CM = 360000
PH_LABEL = {
    'title': 'Title', 'ctrTitle': 'Centered title', 'subTitle': 'Subtitle',
    'body': 'Body', 'obj': 'Content/Object', 'pic': 'Picture', 'tbl': 'Table',
    'chart': 'Chart', 'dgm': 'Diagram', 'clipArt': 'Clip art', 'media': 'Media',
    'sldNum': 'Slide number', 'ftr': 'Footer', 'hdr': 'Header', 'dt': 'Date',
    None: 'Content/Object (default)',
}


def q(tag):
    pfx, local = tag.split(':')
    return '{%s}%s' % (NS[pfx], local)


def main():
    if not PATH.exists():
        sys.exit(f"Template not found: {PATH}")
    z = zipfile.ZipFile(str(PATH))
    names = z.namelist()
    out = {'source_file': str(PATH)}

    # ---- slide size ----
    pres = ET.fromstring(z.read('ppt/presentation.xml'))
    sldSz = pres.find('p:sldSz', NS)
    cx, cy = int(sldSz.get('cx')), int(sldSz.get('cy'))
    out['slide_size'] = {
        'width_in': round(cx / EMU_PER_IN, 3), 'height_in': round(cy / EMU_PER_IN, 3),
        'width_cm': round(cx / EMU_PER_CM, 2), 'height_cm': round(cy / EMU_PER_CM, 2),
        'aspect': '16:9' if abs(cx / cy - 16 / 9) < 0.02 else (
            '4:3' if abs(cx / cy - 4 / 3) < 0.02 else 'custom'),
        'emu': [cx, cy],
    }

    # ---- resolve layouts in master order ----
    def read_rels(part):
        d = part.rsplit('/', 1)
        relpath = (d[0] + '/_rels/' + d[1] + '.rels') if len(d) == 2 else '_rels/' + d[0] + '.rels'
        if relpath not in names:
            return {}, d[0]
        root = ET.fromstring(z.read(relpath))
        return {rel.get('Id'): rel.get('Target') for rel in root}, d[0]

    def norm(base_dir, target):
        stack = []
        for p in (base_dir + '/' + target).split('/'):
            if p == '..':
                stack.pop()
            elif p not in ('.', ''):
                stack.append(p)
        return '/'.join(stack)

    pres_rels, pres_base = read_rels('ppt/presentation.xml')
    master_targets = [norm(pres_base, pres_rels[m.get(q('r:id'))])
                      for m in pres.findall('p:sldMasterIdLst/p:sldMasterId', NS)]

    layouts_ordered = []
    for mt in master_targets:
        mroot = ET.fromstring(z.read(mt))
        mrels, mbase = read_rels(mt)
        for lid in mroot.findall('p:sldLayoutIdLst/p:sldLayoutId', NS):
            layouts_ordered.append(norm(mbase, mrels[lid.get(q('r:id'))]))

    layouts = []
    for i, lt in enumerate(layouts_ordered):
        lroot = ET.fromstring(z.read(lt))
        cSld = lroot.find('p:cSld', NS)
        phs = []
        for sp in lroot.findall('.//p:sp', NS):
            ph = sp.find('.//p:ph', NS)
            if ph is None:
                continue
            cNvPr = sp.find('.//p:cNvPr', NS)
            phs.append({
                'idx': ph.get('idx', '0'), 'type': ph.get('type'),
                'label': PH_LABEL.get(ph.get('type'), ph.get('type')),
                'name': cNvPr.get('name') if cNvPr is not None else None,
            })
        layouts.append({
            'index': i,
            'name': cSld.get('name') if cSld is not None else None,
            'file': lt, 'placeholders': phs,
        })
    out['layouts'] = layouts

    # ---- theme fonts + colours ----
    theme_files = sorted(n for n in names if re.match(r'ppt/theme/theme\d+\.xml$', n))
    if theme_files:
        troot = ET.fromstring(z.read(theme_files[0]))
        out['theme_name'] = troot.get('name')
        fonts = {}
        fs = troot.find('.//a:fontScheme', NS)
        if fs is not None:
            for slot in ('majorFont', 'minorFont'):
                el = fs.find('a:' + slot + '/a:latin', NS)
                if el is not None:
                    fonts[slot] = el.get('typeface')
        out['fonts'] = fonts
        colors = {}
        clr = troot.find('.//a:clrScheme', NS)
        if clr is not None:
            for c in clr:
                srgb, sysc = c.find('a:srgbClr', NS), c.find('a:sysClr', NS)
                if srgb is not None:
                    colors[c.tag.split('}')[1]] = '#' + srgb.get('val').upper()
                elif sysc is not None:
                    colors[c.tag.split('}')[1]] = '#' + (sysc.get('lastClr') or sysc.get('val')).upper()
        out['theme_colors'] = colors

    # ---- company (sanity check it's the right file) ----
    if 'docProps/app.xml' in names:
        aroot = ET.fromstring(z.read('docProps/app.xml'))
        comp = aroot.find('{http://schemas.openxmlformats.org/officeDocument/2006/extended-properties}Company')
        out['company'] = comp.text if comp is not None else None

    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
