#!/usr/bin/env python3
"""Conference figure: Himalayan salt-trade geography."""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from matplotlib.patches import Ellipse, Polygon, Rectangle

OUT = Path(__file__).resolve().parent
BBOX = (72.0, 104.5, 26.0, 38.8)
OVERVIEW_BBOX = (27.0, 146.0, 17.0, 61.0)
MEAN_LAT = 32.5

COLORS = {
    "land": "#fbfaf6",
    "border": "#cfc8bc",
    "grid": "#e9e3d7",
    "salt": "#007c89",
    "source_fill": "#d9f2ef",
    "hub": "#30251f",
    "town": "#5f554f",
    "monastery": "#8b5a2b",
    "pass": "#8a2f3b",
    "core": "#b14a2f",
    "context": "#66788a",
    "zone": "#f0c36a",
    "highland": "#ead9bd",
}

PLACES = {
    "Srinagar": (74.80, 34.08, "hub"),
    "Leh": (77.58, 34.16, "hub"),
    "Gartok": (80.37, 31.73, "hub"),
    "Shigatse": (88.88, 29.27, "hub"),
    "Gyantse": (89.60, 28.95, "hub"),
    "Lhasa": (91.12, 29.65, "hub"),
    "Chamdo": (97.17, 31.14, "hub"),
    "Xining / Sining": (101.78, 36.62, "hub"),
    "Kathmandu": (85.32, 27.71, "hub"),
    "Mandi": (76.93, 31.71, "town"),
    "Skardu / Baltistan": (75.63, 35.30, "town"),
    "Kargil": (76.13, 34.56, "town"),
    "Likir": (77.17, 34.31, "town"),
    "Padum / Zanskar": (76.88, 33.47, "town"),
    "Rudok": (79.70, 33.42, "town"),
    "Rampur Bushahr": (77.63, 31.45, "town"),
    "Joshimath": (79.56, 30.56, "town"),
    "Almora": (79.65, 29.59, "town"),
    "Simikot / Humla": (81.82, 29.97, "town"),
    "Purang / Taklakot": (81.18, 30.15, "town"),
    "Dunai / Dolpo": (82.90, 28.94, "town"),
    "Batang": (99.10, 30.00, "town"),
    "Kangding / Tachienlu": (101.96, 30.05, "town"),
    "Tso Kar": (77.983, 33.300, "salt"),
    "Drang salt mine": (76.94976, 31.80398, "salt"),
    "Guma salt mine": (76.86875, 31.99685, "salt"),
    "Da Qaidam / Tsaidam": (95.25444, 37.83194, "salt"),
    "Qinghai Lake": (100.19, 36.84, "salt"),
    "Gyaring-Ngoring Tso": (97.49, 34.90, "salt"),
    "Siling Co": (89.05, 31.78, "salt"),
    "Namtso": (90.55, 30.70, "salt"),
    "Yanjing / Tsakhalho": (98.60, 29.05, "salt"),
    "Thugje Gompa": (78.05, 33.27, "monastery"),
    "Hemis Gompa": (77.70, 33.91, "monastery"),
    "Korzok": (78.26, 32.97, "monastery"),
    "Shipki La": (78.75, 31.816667, "pass"),
    "Mana Pass": (79.4166, 31.06874, "pass"),
    "Niti Pass": (79.875, 30.9661, "pass"),
    "Taglang La": (77.78, 33.51, "pass"),
}

LABEL_OFFSETS = {
    "Srinagar": (0.18, -0.32),
    "Leh": (0.18, 0.25),
    "Gartok": (0.20, -0.25),
    "Shigatse": (-1.45, 0.10),
    "Gyantse": (-1.20, -0.45),
    "Lhasa": (0.22, 0.20),
    "Chamdo": (0.24, 0.20),
    "Xining / Sining": (0.25, 0.20),
    "Kathmandu": (0.22, -0.35),
    "Mandi": (-1.15, 0.15),
    "Skardu / Baltistan": (0.22, 0.15),
    "Kargil": (0.20, 0.15),
    "Likir": (-0.70, 0.18),
    "Padum / Zanskar": (-1.65, -0.30),
    "Rudok": (0.20, 0.18),
    "Rampur Bushahr": (-2.15, -0.20),
    "Joshimath": (-1.40, -0.25),
    "Almora": (-1.10, -0.30),
    "Simikot / Humla": (-1.35, 0.18),
    "Purang / Taklakot": (0.22, -0.30),
    "Dunai / Dolpo": (0.20, -0.20),
    "Batang": (0.20, 0.15),
    "Kangding / Tachienlu": (0.20, -0.30),
    "Tso Kar": (0.20, -0.35),
    "Drang salt mine": (0.20, -0.26),
    "Guma salt mine": (0.32, 0.04),
    "Da Qaidam / Tsaidam": (-2.10, 0.22),
    "Qinghai Lake": (-1.85, -0.32),
    "Gyaring-Ngoring Tso": (0.22, 0.22),
    "Siling Co": (0.24, 0.22),
    "Namtso": (-1.30, 0.18),
    "Yanjing / Tsakhalho": (0.22, -0.35),
    "Thugje Gompa": (0.18, 0.18),
    "Hemis Gompa": (0.18, -0.28),
    "Korzok": (0.18, -0.24),
    "Shipki La": (0.20, 0.20),
    "Mana Pass": (0.20, -0.24),
    "Niti Pass": (0.20, 0.18),
    "Taglang La": (-1.05, 0.18),
}

ROUTES = [
    ("Kashmir-Ladakh-Rupshu/Ngari", "core", ["Srinagar", "Kargil", "Leh", "Tso Kar", "Rudok", "Gartok"]),
    ("Baltistan-Zanskar-Ladakh exchange", "core", ["Skardu / Baltistan", "Kargil", "Padum / Zanskar", "Tso Kar", "Leh"]),
    ("Bushahr-Shipki-Gartok", "core", ["Rampur Bushahr", "Shipki La", "Gartok"]),
    ("Garhwal-Bhotia via Mana", "core", ["Almora", "Joshimath", "Mana Pass", "Gartok"]),
    ("Garhwal-Bhotia via Niti", "core", ["Almora", "Joshimath", "Niti Pass", "Gartok"]),
    ("Humla-Purang salt circuit", "core", ["Simikot / Humla", "Purang / Taklakot", "Gartok"]),
    ("Nepal-central Tibet context", "context", ["Kathmandu", "Gyantse", "Shigatse", "Lhasa", "Chamdo"]),
    ("Kham/Tsakhalho context", "context", ["Chamdo", "Yanjing / Tsakhalho", "Batang", "Kangding / Tachienlu"]),
    ("Amdo/Qaidam lake belt", "context", ["Xining / Sining", "Qinghai Lake", "Da Qaidam / Tsaidam", "Gyaring-Ngoring Tso"]),
]

ZONES = [
    ("Western Changthang / Rupshu", 78.3, 33.3, 3.4, 1.5, 8),
    ("Mandi salt mines", 76.91, 31.90, 1.15, 0.75, -8),
    ("Central Tibetan lake belt", 89.8, 31.2, 3.4, 1.8, 0),
    ("Tsakhalho salt pans", 98.5, 29.5, 2.2, 1.6, -18),
    ("Amdo-Qaidam sources", 97.8, 36.9, 6.0, 2.0, -6),
]

REGIONS = [
    ("Kashmir", 74.6, 34.9),
    ("Ladakh", 77.7, 34.7),
    ("Zanskar", 76.5, 33.0),
    ("Rupshu / Changthang", 79.0, 33.0),
    ("Western Tibet / Ngari", 81.5, 31.2),
    ("Garhwal-Kumaon", 79.0, 29.3),
    ("Nepal Himalaya", 83.6, 27.8),
    ("Central Tibet", 90.1, 30.2),
    ("Kham / Tsakhalho", 98.6, 30.4),
    ("Amdo / Qinghai", 99.4, 37.5),
]

MAIN_LABELS = set(PLACES) - {"Likir", "Hemis Gompa", "Thugje Gompa", "Korzok", "Taglang La"}
DISPLAY_NAMES = {
    "Drang salt mine": "Drang",
    "Guma salt mine": "Guma",
}

OVERVIEW_MARKETS = [
    ("Moscow", 37.62, 55.75),
    ("Baghdad", 44.37, 33.32),
    ("Astrakhan", 48.04, 46.35),
    ("Isfahan", 51.67, 32.65),
    ("Orenburg", 55.10, 51.77),
    ("Herat", 62.20, 34.35),
    ("Bukhara", 64.42, 39.77),
    ("Samarkand", 66.97, 39.65),
    ("Turkistan", 68.27, 43.30),
    ("Almaty", 76.89, 43.24),
    ("Kokand", 70.94, 40.53),
    ("Kashgar", 75.99, 39.47),
    ("Leh", *PLACES["Leh"][:2]),
    ("Gartok", *PLACES["Gartok"][:2]),
    ("Kucha", 82.96, 41.72),
    ("Turpan", 89.19, 42.95),
    ("Khovd", 91.64, 48.01),
    ("Dunhuang", 94.66, 40.14),
    ("Irkutsk", 104.30, 52.29),
    ("Kyakhta", 106.45, 50.36),
    ("Urga", 106.92, 47.92),
    ("Xi'an", 108.94, 34.34),
    ("Zigong", 104.78, 29.34),
    ("Tianjin", 117.20, 39.08),
    ("Yangzhou", 119.43, 32.39),
    ("Guangzhou", 113.26, 23.13),
    ("Edo / Tokyo", 139.69, 35.69),
    ("Osaka", 135.50, 34.69),
    ("Khambhat", 72.62, 22.32),
    ("Surat", 72.83, 21.17),
    ("Kolkata", 88.36, 22.57),
    ("Dhaka", 90.41, 23.81),
    ("Mandalay", 96.08, 21.96),
]

OVERVIEW_MARKET_OFFSETS = {
    "Moscow": (1.0, -0.8),
    "Baghdad": (-1.0, -1.0),
    "Astrakhan": (1.0, -0.8),
    "Isfahan": (1.0, -0.7),
    "Orenburg": (1.0, 0.8),
    "Herat": (-1.0, 1.0),
    "Bukhara": (-1.0, 1.0),
    "Samarkand": (1.0, -0.8),
    "Turkistan": (-1.0, 1.0),
    "Almaty": (1.0, 0.8),
    "Kokand": (-1.0, 1.0),
    "Kashgar": (1.0, 0.8),
    "Leh": (-1.0, -0.8),
    "Gartok": (1.0, -0.8),
    "Kucha": (1.0, 0.8),
    "Turpan": (1.0, 0.8),
    "Khovd": (-1.0, 0.8),
    "Dunhuang": (1.0, 0.8),
    "Irkutsk": (1.0, 0.8),
    "Kyakhta": (-1.0, 0.8),
    "Urga": (1.0, -0.8),
    "Xi'an": (1.0, 0.8),
    "Zigong": (1.0, -0.8),
    "Tianjin": (1.0, 0.8),
    "Yangzhou": (1.0, -0.8),
    "Guangzhou": (1.0, -0.8),
    "Edo / Tokyo": (-1.0, 0.8),
    "Osaka": (-1.0, -0.8),
    "Khambhat": (-1.0, 1.0),
    "Surat": (1.0, -0.8),
    "Kolkata": (-1.0, -0.8),
    "Dhaka": (1.0, 0.8),
    "Mandalay": (1.0, -0.8),
}


def xy(name: str) -> tuple[float, float]:
    lon, lat, _kind = PLACES[name]
    return lon, lat


def clipped(coords, bbox=BBOX):
    xmin, xmax, ymin, ymax = bbox
    return any(xmin - 1 <= x <= xmax + 1 and ymin - 1 <= y <= ymax + 1 for x, y in coords)


def draw_geojson(ax, bbox=BBOX, lw=0.55, fill=False):
    path = OUT / "ne_110m_admin_0_countries.geojson"
    if not path.exists():
        return
    data = json.loads(path.read_text())
    for feature in data["features"]:
        geom = feature["geometry"]
        polygons = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        for polygon in polygons:
            exterior = polygon[0]
            if not clipped(exterior, bbox):
                continue
            xs, ys = zip(*exterior)
            if fill:
                ax.fill(xs, ys, facecolor="#f4efe7", edgecolor=COLORS["border"], lw=lw, zorder=1)
            else:
                ax.plot(xs, ys, color=COLORS["border"], lw=lw, zorder=1)


def draw_route(ax, route):
    label, kind, names = route
    xs, ys = zip(*(xy(name) for name in names))
    if kind == "core":
        ax.plot(xs, ys, color=COLORS["core"], lw=1.7, solid_capstyle="round", zorder=4)
    else:
        ax.plot(xs, ys, color=COLORS["context"], lw=1.15, ls=(0, (3, 3)), zorder=3)


def label(ax, name, lon, lat, color):
    dx, dy = LABEL_OFFSETS.get(name, (0.18, 0.18))
    ax.text(
        lon + dx,
        lat + dy,
        DISPLAY_NAMES.get(name, name),
        fontsize=7.2,
        fontweight="bold" if PLACES[name][2] in {"hub", "salt"} else "normal",
        color=color,
        ha="left",
        va="center",
        path_effects=[pe.withStroke(linewidth=3, foreground=COLORS["land"])],
        zorder=8,
    )


def draw_places(ax):
    markers = {
        "hub": dict(marker="*", s=92, facecolors="white", edgecolors=COLORS["hub"], linewidths=1.0),
        "town": dict(marker="o", s=24, facecolors=COLORS["land"], edgecolors=COLORS["town"], linewidths=0.9),
        "salt": dict(marker="D", s=52, facecolors=COLORS["source_fill"], edgecolors=COLORS["salt"], linewidths=1.1),
        "monastery": dict(marker="s", s=28, facecolors="#fff7e8", edgecolors=COLORS["monastery"], linewidths=0.9),
        "pass": dict(marker="^", s=45, facecolors="white", edgecolors=COLORS["pass"], linewidths=1.0),
    }
    for name, (lon, lat, kind) in PLACES.items():
        ax.scatter([lon], [lat], zorder=6, **markers[kind])
        if name in MAIN_LABELS:
            label(ax, name, lon, lat, COLORS[kind if kind in COLORS else "town"])


def draw_zones(ax):
    for name, lon, lat, width, height, angle in ZONES:
        ax.add_patch(
            Ellipse(
                (lon, lat),
                width,
                height,
                angle=angle,
                facecolor=COLORS["zone"],
                edgecolor="#c99529",
                alpha=0.16,
                lw=0.8,
                zorder=2,
            )
        )
        if name != "Mandi salt mines":
            ax.text(
                lon,
                lat + height * 0.42,
                name,
                fontsize=6.5,
                color="#72551d",
                ha="center",
                va="center",
                path_effects=[pe.withStroke(linewidth=3, foreground=COLORS["land"])],
                zorder=5,
            )


def setup_ax(ax):
    xmin, xmax, ymin, ymax = BBOX
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_facecolor(COLORS["land"])
    ax.set_aspect(1 / math.cos(math.radians(MEAN_LAT)))
    ax.set_xticks(range(72, 105, 4))
    ax.set_yticks(range(26, 39, 2))
    ax.set_xticklabels([f"{x}°E" for x in range(72, 105, 4)], fontsize=8)
    ax.set_yticklabels([f"{y}°N" for y in range(26, 39, 2)], fontsize=8)
    ax.grid(color=COLORS["grid"], lw=0.45, zorder=0)
    for spine in ax.spines.values():
        spine.set_linewidth(0.8)
        spine.set_color("#332c29")


def draw_region_context(ax):
    highland = [
        (73.5, 33.0),
        (78.0, 35.2),
        (84.0, 33.5),
        (91.0, 32.3),
        (98.5, 33.6),
        (103.0, 31.2),
        (100.5, 29.1),
        (92.0, 29.0),
        (84.5, 28.2),
        (77.0, 30.2),
    ]
    ax.add_patch(Polygon(highland, closed=True, facecolor=COLORS["highland"], edgecolor="none", alpha=0.18, zorder=1.5))
    for text, lon, lat in REGIONS:
        ax.text(
            lon,
            lat,
            text,
            fontsize=7.8,
            fontstyle="italic",
            color="#8c8175",
            alpha=0.82,
            ha="center",
            va="center",
            path_effects=[pe.withStroke(linewidth=3, foreground=COLORS["land"])],
            zorder=3,
        )


def draw_north_and_scale(ax):
    ax.annotate("", xy=(73.0, 37.9), xytext=(73.0, 36.9), arrowprops=dict(arrowstyle="-|>", lw=0.9, color="#332c29"))
    ax.text(73.0, 36.75, "N", ha="center", va="top", fontsize=9, fontweight="bold")
    km = 500
    lon_len = km / (111.32 * math.cos(math.radians(31.0)))
    x0, y0 = 73.0, 26.55
    ax.plot([x0, x0 + lon_len], [y0, y0], color="#332c29", lw=1.2, solid_capstyle="butt")
    ax.plot([x0, x0], [y0 - 0.05, y0 + 0.05], color="#332c29", lw=1.0)
    ax.plot([x0 + lon_len, x0 + lon_len], [y0 - 0.05, y0 + 0.05], color="#332c29", lw=1.0)
    ax.text(x0 + lon_len / 2, y0 + 0.15, "500 km", ha="center", va="bottom", fontsize=7)


def draw_overview_inset(fig):
    ax = fig.add_axes([0.375, 0.675, 0.25, 0.19])
    ax.set_facecolor("#cfe8ef")
    ax.set_xlim(OVERVIEW_BBOX[0], OVERVIEW_BBOX[1])
    ax.set_ylim(OVERVIEW_BBOX[2], OVERVIEW_BBOX[3])
    ax.set_aspect(1 / math.cos(math.radians(35)))
    draw_geojson(ax, OVERVIEW_BBOX, lw=0.35, fill=True)
    ax.add_patch(
        Rectangle(
            (BBOX[0], BBOX[2]),
            BBOX[1] - BBOX[0],
            BBOX[3] - BBOX[2],
            fill=False,
            edgecolor="#c9252d",
            lw=1.6,
            zorder=4,
        )
    )
    for text, lon, lat in OVERVIEW_MARKETS:
        dx, dy = OVERVIEW_MARKET_OFFSETS[text]
        ax.plot(lon, lat, marker="*", ms=3.2, mfc="#fff7e8", mec="#8a2f3b", mew=0.45, color="#8a2f3b", zorder=5)
        ax.text(
            lon + dx,
            lat + dy,
            text,
            fontsize=3.6,
            fontweight="bold",
            color="#3a302c",
            ha="right" if dx < 0 else "left",
            va="center",
            path_effects=[pe.withStroke(linewidth=1.1, foreground="#f4efe7")],
            zorder=6,
        )
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_linewidth(0.8)
        spine.set_color("#554c46")


def draw_inset(fig):
    ax = fig.add_axes([0.115, 0.132, 0.235, 0.255])
    ax.set_facecolor("#fffdfa")
    ax.set_xlim(76.6, 80.0)
    ax.set_ylim(32.6, 34.6)
    ax.set_aspect(1 / math.cos(math.radians(33.5)))
    ax.grid(color=COLORS["grid"], lw=0.35)
    for route in ROUTES[:2]:
        draw_route(ax, route)
    inset_offsets = {
        "Leh": (0.05, 0.09),
        "Likir": (0.04, 0.08),
        "Hemis Gompa": (0.06, 0.07),
        "Taglang La": (0.06, 0.06),
        "Thugje Gompa": (0.07, -0.08),
        "Tso Kar": (0.08, 0.07),
        "Korzok": (0.05, -0.08),
        "Rudok": (0.05, 0.08),
        "Padum / Zanskar": (0.05, 0.08),
    }
    for name in ["Leh", "Likir", "Hemis Gompa", "Taglang La", "Thugje Gompa", "Tso Kar", "Korzok", "Rudok", "Padum / Zanskar"]:
        lon, lat, kind = PLACES[name]
        marker = {"salt": "D", "monastery": "s", "pass": "^", "hub": "*"}.get(kind, "o")
        ax.scatter([lon], [lat], s=32 if kind != "hub" else 60, marker=marker, facecolors="white", edgecolors=COLORS.get(kind, COLORS["town"]), lw=0.8, zorder=6)
        dx, dy = inset_offsets[name]
        ax.text(lon + dx, lat + dy, name.replace(" / Zanskar", ""), fontsize=5.6, color="#3b3430", path_effects=[pe.withStroke(linewidth=2, foreground="#fffdfa")])
    ax.set_title("Rupshu-Tso Kar Detail", fontsize=8, fontweight="bold", pad=3)
    ax.set_xticks([77, 78, 79, 80])
    ax.set_yticks([33, 34])
    ax.tick_params(labelsize=6, length=2)
    for spine in ax.spines.values():
        spine.set_linewidth(0.8)
        spine.set_color("#554c46")


def main():
    fig, ax = plt.subplots(figsize=(13.8, 8.2), dpi=300)
    setup_ax(ax)
    draw_geojson(ax)
    draw_region_context(ax)
    draw_zones(ax)
    for route in ROUTES:
        draw_route(ax, route)
    draw_places(ax)
    draw_north_and_scale(ax)
    draw_overview_inset(fig)
    draw_inset(fig)

    handles = [
        Line2D([0], [0], marker="*", color="none", markerfacecolor="white", markeredgecolor=COLORS["hub"], markersize=10, label="Major market / hub"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLORS["land"], markeredgecolor=COLORS["town"], markersize=6, label="Trade town / locality"),
        Line2D([0], [0], marker="D", color="none", markerfacecolor=COLORS["source_fill"], markeredgecolor=COLORS["salt"], markersize=7, label="Salt source / lake / mine"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor="#fff7e8", markeredgecolor=COLORS["monastery"], markersize=6, label="Monastery / institution"),
        Line2D([0], [0], marker="^", color="none", markerfacecolor="white", markeredgecolor=COLORS["pass"], markersize=7, label="Mountain pass"),
        Line2D([0], [0], color=COLORS["core"], lw=1.8, label="Core source-attested corridor"),
        Line2D([0], [0], color=COLORS["context"], lw=1.2, ls=(0, (3, 3)), label="Broader trade context"),
        Line2D([0], [0], color="#c99529", lw=5, alpha=0.22, label="Salt-producing zone"),
    ]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=4, frameon=False, fontsize=8.5)

    fig.suptitle("Himalayan Salt Trade Geography", fontsize=17, fontweight="bold", y=0.985)
    ax.set_title(
        "Kashmir, Ladakh, the Western Himalayas, Tibet, Qinghai and Kham",
        fontsize=10.5,
        pad=16,
        color="#3b3430",
    )
    fig.text(
        0.5,
        0.025,
        "Evidence base: mock paper, cleaned salt graph evidence, corpus summaries, and modern gazetteer coordinates. Historical regions are labels; route lines are schematic corridor families, not surveyed caravan tracks.",
        ha="center",
        va="bottom",
        fontsize=8,
        color="#625a54",
    )
    fig.subplots_adjust(left=0.055, right=0.99, top=0.90, bottom=0.18)

    for ext in ("png", "pdf", "svg"):
        fig.savefig(OUT / f"himalayan_salt_trade_geography_conference.{ext}", bbox_inches="tight")

    png = OUT / "himalayan_salt_trade_geography_conference.png"
    assert png.exists() and png.stat().st_size > 100_000
    assert all(BBOX[0] <= lon <= BBOX[1] and BBOX[2] <= lat <= BBOX[3] for lon, lat, _ in PLACES.values())
    assert [name for name, lon, lat in OVERVIEW_MARKETS if BBOX[0] <= lon <= BBOX[1] and BBOX[2] <= lat <= BBOX[3]] == ["Leh", "Gartok"]
    assert PLACES["Drang salt mine"] != PLACES["Guma salt mine"]
    assert PLACES["Mana Pass"] != PLACES["Niti Pass"]


if __name__ == "__main__":
    main()
