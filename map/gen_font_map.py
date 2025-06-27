#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import io
import base64
import urllib.request
from fontTools.ttLib import TTFont

BLOCKS_URL = "https://www.unicode.org/Public/draft/ucd/Blocks.txt"
UNDEFINED_BLOCK_NAME = "Undefined Characters"

def fetch_blocks():
    resp = urllib.request.urlopen(BLOCKS_URL)
    data = resp.read().decode("utf-8")
    blocks = []
    for line in data.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        rng, name = [p.strip() for p in line.split(";")]
        start, end = [int(p, 16) for p in rng.split("..")]
        blocks.append((start, end, name))
    return blocks

def find_block(codepoint, blocks):
    for start, end, name in blocks:
        if start <= codepoint <= end:
            return name
    return None  # 不再返回 "No_Block"，而是 None

def extract_cmap(fontpath):
    tt = TTFont(fontpath)
    cmap = {}
    for table in tt["cmap"].tables:
        if table.isUnicode():
            cmap.update(table.cmap)
    return sorted(set(cmap.keys()))

def make_html(fontpaths, outpath):
    blocks = fetch_blocks()
    PAGE_SIZE = 500

    fonts_data = []
    for i, fontpath in enumerate(fontpaths):
        print(f"正在处理字体 {i+1}/{len(fontpaths)}: {fontpath}")
        codepoints = extract_cmap(fontpath)

        # 按 block 分组
        block_map = {}
        for cp in codepoints:
            blk = find_block(cp, blocks)
            blk_name = blk if blk is not None else UNDEFINED_BLOCK_NAME
            block_map.setdefault(blk_name, []).append(cp)

        # 读取并 Base64 编码字体
        fontdata = open(fontpath, "rb").read()
        b64 = base64.b64encode(fontdata).decode("ascii")
        fontname = os.path.basename(fontpath)

        fonts_data.append({
            'path': fontpath,
            'name': fontname,
            'base64': b64,
            'codepoints': codepoints,
            'block_map': block_map,
            'id': f'font_{i}'
        })

    with open(outpath, "w", encoding="utf-8") as f:
        # HTML 头部
        f.write(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>Font Unicode Map - Multiple Fonts</title>
  <link rel="stylesheet" href="main.css">
  <style>
""")
        # 动态注入 @font-face
        for font_data in fonts_data:
            f.write(f"""
    .{font_data['id']} .glyph {{
      font-family: '{font_data['id']}';
    }}
    @font-face {{
      font-family: '{font_data['id']}';
      src: url(data:font/ttf;base64,{font_data['base64']}) format('truetype');
      font-weight: normal;
      font-style: normal;
    }}""")
        f.write("""
  </style>
  <link rel="stylesheet" href="scrollbar.css">
  <script defer="defer" src="main.js"></script>
</head>
<body>
  <div class="tabs">
    <ul class="tab-list">
""")
        # 生成标签页
        for i, font_data in enumerate(fonts_data):
            active = "active" if i==0 else ""
            f.write(f'      <li class="tab-item"><a href="javascript:void(0)" class="tab-link {active}" onclick="switchFont(\'{font_data["id"]}\')">{font_data["name"]}</a></li>\n')
        f.write("""    </ul>
  </div>
""")
        # 为每个字体生成内容
        for idx, font_data in enumerate(fonts_data):
            active = "active" if idx==0 else ""
            fid = font_data['id']
            fmap = font_data['block_map']
            f.write(f'  <div id="{fid}" class="font-content {active} {fid}">\n')
            f.write('    <div class="container">\n')
            f.write('      <nav class="nav">\n')
            # 先 Undefined Characters
            if UNDEFINED_BLOCK_NAME in fmap:
                cnt = len(fmap[UNDEFINED_BLOCK_NAME])
                safe = UNDEFINED_BLOCK_NAME.replace(" ", "_")
                f.write(f'        <a href="#{fid}_blk_{safe}">{UNDEFINED_BLOCK_NAME} ({cnt})</a>\n')
            # 再常规模块
            for start, end, name in blocks:
                if name in fmap:
                    cnt = len(fmap[name])
                    safe = name.replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")
                    f.write(f'        <a href="#{fid}_blk_{safe}">{name} ({cnt})</a>\n')
            f.write('      </nav>\n')
            f.write('      <div class="main">\n')
            # 先 Undefined Characters 区块内容
            if UNDEFINED_BLOCK_NAME in fmap:
                cps = fmap[UNDEFINED_BLOCK_NAME]
                safe = UNDEFINED_BLOCK_NAME.replace(" ", "_")
                anchor = f"{fid}_blk_{safe}"
                f.write(f'        <section id="{anchor}">\n')
                f.write(f'          <h2>{UNDEFINED_BLOCK_NAME}, {len(cps)} items</h2>\n')
                # 分页逻辑
                if len(cps) > PAGE_SIZE:
                    pages = (len(cps)+PAGE_SIZE-1)//PAGE_SIZE
                    f.write('          <div class="pagination">\n')
                    for p in range(1, pages+1):
                        f.write(f'            <button class="page-btn-{p}" onclick="showPage(\'{fid}\', \'{anchor}\', {p})">{p}</button>\n')
                    f.write('          </div>\n')
                    for p in range(1, pages+1):
                        start_i = (p-1)*PAGE_SIZE
                        end_i = min(start_i+PAGE_SIZE, len(cps))
                        page_cps = cps[start_i:end_i]
                        f.write(f'          <div class="page page-{p}">\n            <div class="glyph-grid">\n')
                        for cp in page_cps:
                            hx = f"{cp:04X}"
                            f.write('              <div class="glyph-item">\n')
                            f.write(f'                <div class="codepoint">${hx}</div>\n')
                            f.write(f'                <div class="glyph">&#x{hx};</div>\n')
                            f.write('              </div>\n')
                        f.write('            </div>\n          </div>\n')
                else:
                    f.write('          <div class="glyph-grid">\n')
                    for cp in cps:
                        hx = f"{cp:04X}"
                        f.write('            <div class="glyph-item">\n')
                        f.write(f'              <div class="codepoint">${hx}</div>\n')
                        f.write(f'              <div class="glyph">&#x{hx};</div>\n')
                        f.write('            </div>\n')
                    f.write('          </div>\n')
                f.write('        </section>\n')
            # 再常规模块内容
            for start, end, name in blocks:
                if name not in fmap:
                    continue
                cps = fmap[name]
                safe = name.replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")
                anchor = f"{fid}_blk_{safe}"
                f.write(f'        <section id="{anchor}">\n')
                f.write(f'          <h2>{name} (U+{start:04X}..U+{end:04X}), {len(cps)} items</h2>\n')
                if len(cps) > PAGE_SIZE:
                    pages = (len(cps)+PAGE_SIZE-1)//PAGE_SIZE
                    f.write('          <div class="pagination">\n')
                    for p in range(1, pages+1):
                        f.write(f'            <button class="page-btn-{p}" onclick="showPage(\'{fid}\', \'{anchor}\', {p})">{p}</button>\n')
                    f.write('          </div>\n')
                    for p in range(1, pages+1):
                        start_i = (p-1)*PAGE_SIZE
                        end_i = min(start_i+PAGE_SIZE, len(cps))
                        page_cps = cps[start_i:end_i]
                        f.write(f'          <div class="page page-{p}">\n            <div class="glyph-grid">\n')
                        for cp in page_cps:
                            hx = f"{cp:04X}"
                            f.write('              <div class="glyph-item">\n')
                            f.write(f'                <div class="codepoint">${hx}</div>\n')
                            f.write(f'                <div class="glyph">&#x{hx};</div>\n')
                            f.write('              </div>\n')
                        f.write('            </div>\n          </div>\n')
                else:
                    f.write('          <div class="glyph-grid">\n')
                    for cp in cps:
                        hx = f"{cp:04X}"
                        f.write('            <div class="glyph-item">\n')
                        f.write(f'              <div class="codepoint">${hx}</div>\n')
                        f.write(f'              <div class="glyph">&#x{hx};</div>\n')
                        f.write('            </div>\n')
                    f.write('          </div>\n')
                f.write('        </section>\n')
            f.write('      </div>\n    </div>\n  </div>\n')

        f.write("""</body>
</html>
""")

    print(f"已生成：{outpath}")

def main():
    if len(sys.argv) < 3:
        print("用法: python gen_font_map.py output.html font1.ttf [font2.ttf] ...")
        sys.exit(1)
    outpath = sys.argv[1]
    fontpaths = sys.argv[2:]
    print(f"正在处理 {len(fontpaths)} 个字体文件...")
    print("正在下载并解析 Unicode Blocks...")
    make_html(fontpaths, outpath)

if __name__ == "__main__":
    main()