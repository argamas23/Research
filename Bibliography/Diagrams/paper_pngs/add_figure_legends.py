import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
REPO_ROOT = BASE.parents[2]
SOURCE_DIR = REPO_ROOT / 'Mine' / 'outputs' / 'paper_pngs'
FILES = sorted((SOURCE_DIR.glob('*.png') if SOURCE_DIR.exists() else BASE.glob('*.png')))

# Match the project graph styling in Mine/graph_rules.py
NODE_COLORS = {
    'PERSON': '#4c72b0',
    'GROUP': '#8172b2',
    'LOCATION': '#55a868',
    'COMMODITY': '#c44e52',
    'CONCEPT': '#937860',
    'FOCUS': '#ffcc00',
}

EDGE_COLORS = {
    'trades_with': '#2f8f5b',
    'extracts_from': '#b86b2b',
    'taxes': '#c73e3a',
    'licenses': '#7d5cc6',
    'controls': '#8a4a24',
    'governs': '#315f9f',
    'supplies': '#c28f00',
    'depends_on': '#6f7c85',
    'transports_via': '#2f80c0',
    'connects_to': '#2f80c0',
    'monopolizes': '#7f3b3b',
    'disputes': '#d62728',
    'negotiates_with': '#8b6f3d',
}

CIRCUIT_COLORS = {
    'Salt anchor': '#ffcc00',
    'Commodity circuits': '#c44e52',
    'Political economy': '#315f9f',
    'Route/place circuits': '#55a868',
    'Social actors': '#8172b2',
    'Conceptual context': '#937860',
}

BOX_BG = (255, 255, 255, 255)
BOX_BORDER = (120, 126, 132, 230)
TEXT = '#111111'


def font(size: int, bold: bool = False):
    if bold:
        return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', size)
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size)


def add_legend(path: Path):
    img = Image.open(path).convert('RGBA')
    w, h = img.size

    box_w, box_h = 2100, 900
    x0, y0 = w - box_w - 90, h - box_h - 20

    node_items = [
        ('PERSON', NODE_COLORS['PERSON']),
        ('GROUP', NODE_COLORS['GROUP']),
        ('LOCATION', NODE_COLORS['LOCATION']),
        ('COMMODITY', NODE_COLORS['COMMODITY']),
        ('CONCEPT', NODE_COLORS['CONCEPT']),
        ('RESEARCH FOCUS', NODE_COLORS['FOCUS']),
    ]

    # Layout parameters (for measurement)
    x = x0 + 50
    y = y0 + 200
    header_font = font(42, bold=True)
    section_gap = 28
    header_to_items_gap = 48
    item_gap = 72

    # Relation items (needed for measurement)
    relation_items = [
        ('trades_with', EDGE_COLORS['trades_with']),
        ('extracts_from', EDGE_COLORS['extracts_from']),
        ('governs', EDGE_COLORS['governs']),
        ('supplies', EDGE_COLORS['supplies']),
        ('transports_via', EDGE_COLORS['transports_via']),
        ('taxes', EDGE_COLORS['taxes']),
        ('disputes', EDGE_COLORS['disputes']),
        ('licenses', EDGE_COLORS['licenses']),
    ]

    # Measure vertical space required by node and relation columns
    y_nodes_end = y + header_to_items_gap + item_gap * len(node_items)
    y2_start = y0 + 200
    y_rels_end = y2_start + header_to_items_gap + item_gap * len(relation_items)

    content_bottom = max(y_nodes_end, y_rels_end) + 32
    needed_height = content_bottom - y0 + 40
    box_h = max(box_h, int(needed_height))

    # Now create overlay and draw background rectangle and title behind content
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle((x0, y0, x0 + box_w, y0 + box_h), radius=32, fill=BOX_BG, outline=BOX_BORDER, width=6)
    draw.text((x0 + 40, y0 + 30), 'Legend', fill=TEXT, font=font(72, bold=True))

    # Layout parameters (computed to avoid overlaps)
    x = x0 + 50
    y = y0 + 200
    header_font = font(42, bold=True)
    section_gap = 28
    header_to_items_gap = 48
    item_gap = 72

    draw.text((x, y - 60), 'Node types', fill=TEXT, font=header_font)
    y += header_to_items_gap
    for label, color in node_items:
        draw.ellipse((x, y, x + 42, y + 42), fill=color, outline=(0, 0, 0, 170), width=3)
        draw.text((x + 62, y + 2), label, fill=TEXT, font=font(36))
        y += item_gap

    relation_items = [
        ('trades_with', EDGE_COLORS['trades_with']),
        ('extracts_from', EDGE_COLORS['extracts_from']),
        ('governs', EDGE_COLORS['governs']),
        ('supplies', EDGE_COLORS['supplies']),
        ('transports_via', EDGE_COLORS['transports_via']),
        ('taxes', EDGE_COLORS['taxes']),
        ('disputes', EDGE_COLORS['disputes']),
        ('licenses', EDGE_COLORS['licenses']),
    ]

    x2 = x0 + 1050
    y2 = y0 + 200
    draw.text((x2, y2 - 60), 'Relations', fill=TEXT, font=header_font)
    y2 += header_to_items_gap
    for label, color in relation_items:
        draw.line((x2, y2 + 20, x2 + 90, y2 + 20), fill=color, width=10)
        draw.text((x2 + 120, y2), label, fill=TEXT, font=font(32))
        y2 += item_gap

    result = Image.alpha_composite(img, overlay)
    result = result.convert('RGB')
    result.save(path, format='PNG', optimize=True)


for src in FILES:
    dst = BASE / src.name
    if src.resolve() != dst.resolve():
        shutil.copy2(src, dst)
    add_legend(dst)
    print(f'Updated {dst.name} from {src.name}')
