#!/usr/bin/env python3
"""One-shot patch: add two Content collection mods from the 8 Sep 2026 Steam snapshot."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

NEW_EMITTER = (
    '{"t":"Manipulator Beam Emitter","c":"Building, production & storage",'
    '"core":false,"content":true,"cosmetics":false,"id":"3683998684",'
    '"u":"https://steamcommunity.com/sharedfiles/filedetails/?id=3683998684","p":""}'
)
NEW_TEX = (
    '{"t":"Manipulator Beam Emitter Retexture","c":"Textures & retextures",'
    '"core":false,"content":true,"cosmetics":false,"id":"3798109974",'
    '"u":"https://steamcommunity.com/sharedfiles/filedetails/?id=3798109974","p":""}'
)


def must_replace(text, old, new, label):
    if old not in text:
        if new[:40] in text:
            print(f'{label}: already patched')
            return text
        raise SystemExit(f'{label}: needle not found')
    return text.replace(old, new, 1)


def patch_index():
    p = ROOT / 'index.html'
    t = p.read_text(encoding='utf-8')
    if '3683998684' in t and '3798109974' in t and '1015 of 1474' in t:
        print('index.html already patched')
        return
    t = must_replace(
        t,
        'packageId values from RimSort Steam-Workshop-Database where available (1015 of 1472).',
        'packageId values from RimSort Steam-Workshop-Database where available (1015 of 1474).',
        'index footer',
    )
    needle = (
        '{"t":"LusTech VWE Coilguns Retexture","c":"Textures & retextures",'
        '"core":false,"content":true,"cosmetics":false,"id":"3750587891",'
        '"u":"https://steamcommunity.com/sharedfiles/filedetails/?id=3750587891","p":""},'
        '{"t":"Meat on a Stick (Retexture)"'
    )
    insert = (
        '{"t":"LusTech VWE Coilguns Retexture","c":"Textures & retextures",'
        '"core":false,"content":true,"cosmetics":false,"id":"3750587891",'
        '"u":"https://steamcommunity.com/sharedfiles/filedetails/?id=3750587891","p":""},'
        + NEW_TEX + ',' + NEW_EMITTER + ','
        + '{"t":"Meat on a Stick (Retexture)"'
    )
    t = must_replace(t, needle, insert, 'index DATA')
    p.write_text(t, encoding='utf-8')
    print('patched index.html', p.stat().st_size)


def patch_csv():
    p = ROOT / 'backup' / 'progression_packageids.csv'
    t = p.read_text(encoding='utf-8')
    if '3683998684' in t and '3798109974' in t:
        print('csv already patched')
        return
    rows = (
        'Manipulator Beam Emitter,3683998684,,0,1,0,'
        'https://steamcommunity.com/sharedfiles/filedetails/?id=3683998684\n'
        'Manipulator Beam Emitter Retexture,3798109974,,0,1,0,'
        'https://steamcommunity.com/sharedfiles/filedetails/?id=3798109974\n'
    )
    if not t.endswith('\n'):
        t += '\n'
    p.write_text(t + rows, encoding='utf-8')
    print('patched csv')


def patch_txt():
    p = ROOT / 'backup' / 'progression_collections_categorized.txt'
    t = p.read_text(encoding='utf-8')
    if '3683998684' in t and '3798109974' in t:
        print('txt already patched')
        return
    t = must_replace(t, 'Textures & retextures  (70)', 'Textures & retextures  (71)', 'txt tex count')
    t = must_replace(
        t,
        'Building, production & storage  (67)',
        'Building, production & storage  (68)',
        'txt building count',
    )
    t = must_replace(
        t,
        '  - LusTech VWE Coilguns Retexture\n'
        '    [2/3 Content]  https://steamcommunity.com/sharedfiles/filedetails/?id=3750587891\n',
        '  - LusTech VWE Coilguns Retexture\n'
        '    [2/3 Content]  https://steamcommunity.com/sharedfiles/filedetails/?id=3750587891\n'
        '  - Manipulator Beam Emitter Retexture\n'
        '    [2/3 Content]  https://steamcommunity.com/sharedfiles/filedetails/?id=3798109974\n',
        'txt tex item',
    )
    t = must_replace(
        t,
        '  - Logic Switch\n'
        '    [2/3 Content]  https://steamcommunity.com/sharedfiles/filedetails/?id=3723818517\n',
        '  - Logic Switch\n'
        '    [2/3 Content]  https://steamcommunity.com/sharedfiles/filedetails/?id=3723818517\n'
        '  - Manipulator Beam Emitter\n'
        '    [2/3 Content]  https://steamcommunity.com/sharedfiles/filedetails/?id=3683998684\n',
        'txt building item',
    )
    p.write_text(t, encoding='utf-8')
    print('patched categorized txt')


def main():
    patch_index()
    patch_csv()
    patch_txt()
    print('done')


if __name__ == '__main__':
    main()
