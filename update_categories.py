#!/usr/bin/env python3
"""
批量修改产品 MD 文件的 categories 字段
按照 10 个类目 + 1 个其他类目对所有产品进行正确分类

重要：仅修改 YAML front matter 中的 categories 字段
      文件其他所有内容（正文、其他字段、格式、空行等）完全不动
"""

import os
import re
import sys

# ============================================================
# 产品目录路径（相对于仓库根目录）
# ============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_DIR = os.path.join(SCRIPT_DIR, "content", "products")

# ============================================================
# 10 个标准类目 + 1 个其他类目
# ============================================================
#  1. bathroom-accessories    浴室用品
#  2. cleaning-tools          清洁工具
#  3. coffee-tea              咖啡茶具
#  4. cookware-bakeware       锅具烤具
#  5. drinkware-bottles       饮水瓶杯
#  6. home-lifestyle-gifts    家居生活礼品
#  7. kitchen-gadgets         厨房工具
#  8. outdoor-camping         户外露营
#  9. storage-organization    收纳整理
# 10. tableware-dining        餐具餐具
# 11. other                   其他（不在映射表中的产品）
# ============================================================

# ============================================================
# 文件名 → 新类目 映射表
# 从产品分类表单数据提取，共 184 个产品文件
# ============================================================
CATEGORY_MAPPING = {
    # === Bathroom Accessories (5) ===
    "ba-015-stainless-steel-cone-soap-dispenser.md": "bathroom-accessories",
    "ba-017-stainless-steel-spray-bottle.md": "bathroom-accessories",
    "ba-018-stainless-steel-toilet-brush-set-classic.md": "bathroom-accessories",
    "ba-019-stainless-steel-designer-toilet-brush-set.md": "bathroom-accessories",
    "ba-025-ceramic-gold-patterned-soap-dispenser-set.md": "bathroom-accessories",

    # === Cleaning Tools (7) ===
    "ct-001-microfiber-car-cleaning-cloth-blue-super-absorbent-wholesale.md": "cleaning-tools",
    "ct-001-microfiber-flat-floor-mop-set.md": "cleaning-tools",
    "ct-002-microfiber-general-cleaning-cloth-mint-green-quilted-wholesale.md": "cleaning-tools",
    "ct-003-stainless-steel-wire-scrub-cloth-silver-dishwashing-wholesale.md": "cleaning-tools",
    "ct-004-non-woven-perforated-hand-tear-cleaning-cloth-roll-wholesale.md": "cleaning-tools",
    "ct-005-microfiber-coordinated-kitchen-towel-set-color-roll-wholesale.md": "cleaning-tools",
    "ct-006-microfiber-cleaning-gloves-mitts-gray-textured-wholesale.md": "cleaning-tools",

    # === Coffee & Tea Essentials (11) ===
    "dw-010-colorful-enamel-cast-iron-teapot-floral-maple-dragon-bamboo.md": "coffee-tea",
    "dw-011-traditional-black-textured-cast-iron-teapot-hammered-relief.md": "coffee-tea",
    "dw-012-vintage-gold-bronze-cast-iron-teapot-dragon-geometric-relief.md": "coffee-tea",
    "dw-013-green-cast-iron-teapot-bamboo-vertical-stripe-nature.md": "coffee-tea",
    "dw-014-red-cast-iron-teapot-textured-relief-classic-wine-crimson.md": "coffee-tea",
    "dw-015-cast-iron-teapot-warmer-stand-heater-base-electric-candle.md": "coffee-tea",
    "kg-006-electric-coffee-grinder.md": "coffee-tea",
    "kg-007-handheld-electric-milk-frother.md": "coffee-tea",
    "kg-008-pour-over-coffee-filter-set.md": "coffee-tea",
    "kg-009-stainless-steel-mocha-pot.md": "coffee-tea",
    "kg-020-electric-coffee-bean-grinder-spice-mill.md": "coffee-tea",

    # === Cookware & Bakeware (7) ===
    "kg-024-aluminum-nonstick-cooking-pot-fry-pan-set.md": "cookware-bakeware",
    "kg-025-stainless-steel-perforated-baking-steaming-tray.md": "cookware-bakeware",
    "kg-028-stainless-steel-round-deep-fry-basket-wire-mesh-wholesale.md": "cookware-bakeware",
    "kg-029-stainless-steel-square-deep-fry-basket-red-handle-wholesale.md": "cookware-bakeware",
    "kg-030-stainless-steel-non-stick-frying-pan-black-handle-wholesale.md": "cookware-bakeware",
    "kg-031-stainless-steel-wood-handle-wok-cooking-pot-with-lid-wholesale.md": "cookware-bakeware",
    "kg-049-stainless-steel-wok-spatula-turner-cooking-wholesale.md": "cookware-bakeware",

    # === Drinkware & Bottles (52) ===
    "ba-001-40oz-stainless-steel-tumbler-with-handle.md": "drinkware-bottles",
    "ba-002-24oz-stainless-steel-tumbler-with-handle.md": "drinkware-bottles",
    "ba-003-16oz-stainless-steel-compact-tumbler-with-handle.md": "drinkware-bottles",
    "ba-004-40oz-gradient-stainless-steel-tumbler.md": "drinkware-bottles",
    "ba-005-20oz-slim-stainless-steel-tumbler-with-straw.md": "drinkware-bottles",
    "ba-006-hand-blown-glass-decanter-carafe.md": "drinkware-bottles",
    "ba-007-gold-plated-wine-glasses.md": "drinkware-bottles",
    "ba-008-colored-glass-wine-glasses.md": "drinkware-bottles",
    "ba-009-whiskey-glasses-tumblers-set.md": "drinkware-bottles",
    "ba-010-mason-jar-tumbler-with-straw-lid.md": "drinkware-bottles",
    "ba-011-plated-champagne-flutes-colored-stem.md": "drinkware-bottles",
    "ba-012-cartoon-kids-sippy-cup.md": "drinkware-bottles",
    "ba-013-sports-themed-water-bottle.md": "drinkware-bottles",
    "ba-014-gradient-portable-sip-cup.md": "drinkware-bottles",
    "ba-016-stainless-steel-cylindrical-soap-lotion-dispenser.md": "drinkware-bottles",
    "ba-020-ribbed-glass-pitcher-with-metal-lid.md": "drinkware-bottles",
    "ba-021-smoked-glass-tapered-pitcher-with-metal-lid.md": "drinkware-bottles",
    "ba-022-glass-storage-jar-set-with-metal-lid.md": "drinkware-bottles",
    "ba-026-plastic-sport-water-bottle-with-flip-lid-text-animal-design.md": "drinkware-bottles",
    "ba-027-double-wall-glitter-tumbler-dome-lid-straw-fruit-cartoon.md": "drinkware-bottles",
    "ba-028-mini-glitter-tumbler-dome-lid-pearl-bead-cute-character.md": "drinkware-bottles",
    "ba-029-sport-water-bottle-with-timer-dial-panda-clock-design.md": "drinkware-bottles",
    "ba-030-clear-glitter-charm-double-wall-tumbler-heart-rainbow-unicorn.md": "drinkware-bottles",
    "ba-031-silicone-collapsible-foldable-water-bottle-rainbow-macaron.md": "drinkware-bottles",
    "ba-032-geometric-texture-sport-water-bottle-large-capacity-candy-color.md": "drinkware-bottles",
    "ba-033-printed-pattern-sport-water-bottle-carnival-cherry-cartoon.md": "drinkware-bottles",
    "ba-034-stainless-steel-cartoon-insulated-tumbler-large-handle-straw.md": "drinkware-bottles",
    "ba-035-creative-themed-water-bottle-pumpkin-basketball-bear-shape.md": "drinkware-bottles",
    "ba-036-silicone-collapsible-coffee-cup-foldable-travel-mug-multilayer.md": "drinkware-bottles",
    "ba-037-large-capacity-stainless-steel-tumbler-handle-leopard-gray-purple-green.md": "drinkware-bottles",
    "ba-038-gradient-color-sport-water-bottle-large-capacity-handle-lid.md": "drinkware-bottles",
    "ba-039-printed-pattern-stainless-steel-tumbler-bow-stripe-floral-coffee.md": "drinkware-bottles",
    "ba-040-spiral-texture-silicone-collapsible-water-bottle-foldable-pink-purple.md": "drinkware-bottles",
    "ba-041-american-football-shaped-water-bottle-leather-texture-sports-fan.md": "drinkware-bottles",
    "ba-042-large-capacity-sport-water-bottle-handle-lid-blue-purple-pink.md": "drinkware-bottles",
    "ba-043-cartoon-animal-head-kids-stainless-steel-vacuum-bottle-wholesale.md": "drinkware-bottles",
    "ba-044-printed-floral-stainless-steel-vacuum-bottle-flip-lid-wholesale.md": "drinkware-bottles",
    "ba-045-large-capacity-printed-sport-vacuum-bottle-handle-lid-wholesale.md": "drinkware-bottles",
    "ba-046-large-capacity-solid-color-sport-vacuum-bottle-carry-lid-wholesale.md": "drinkware-bottles",
    "ba-047-large-capacity-stainless-base-sport-vacuum-bottle-ring-lid-wholesale.md": "drinkware-bottles",
    "ba-048-large-capacity-tumbler-handle-straw-lid-insulated-cup-wholesale.md": "drinkware-bottles",
    "ba-049-cut-glass-crystal-wine-goblet-whiskey-cocktail-glass-wholesale.md": "drinkware-bottles",
    "ba-050-turkish-style-tulip-glass-teacup-saucer-set-wholesale.md": "drinkware-bottles",
    "ba-051-glass-teacup-coffee-cup-handle-saucer-set-amber-wholesale.md": "drinkware-bottles",
    "ba-052-gold-rim-glass-teacup-coffee-cup-saucer-set-wholesale.md": "drinkware-bottles",
    "ba-055-stainless-steel-cartoon-dog-head-vacuum-bottle-kids-cute-wholesale.md": "drinkware-bottles",
    "ba-056-stainless-steel-cartoon-cat-head-vacuum-bottle-kids-cute-wholesale.md": "drinkware-bottles",
    "ba-057-stainless-steel-cartoon-bear-panda-head-vacuum-bottle-kids-wholesale.md": "drinkware-bottles",
    "ba-058-stainless-steel-cartoon-unicorn-reindeer-head-vacuum-bottle-kids-wholesale.md": "drinkware-bottles",
    "ba-059-stainless-steel-cartoon-farm-animal-head-vacuum-bottle-kids-wholesale.md": "drinkware-bottles",
    "ba-060-stainless-steel-cartoon-animal-head-vacuum-flask-premium-decorated-wholesale.md": "drinkware-bottles",
    "dw-018-sports-water-bottle-shaker-cup-protein-mixer.md": "drinkware-bottles",

    # === Home Lifestyle Gifts (5) ===
    "ba-020-fruit-print-acrylic-handbag-vase.md": "home-lifestyle-gifts",
    "ba-021-solid-color-gradient-acrylic-handbag-vase.md": "home-lifestyle-gifts",
    "ba-022-bow-decor-acrylic-handbag-vase.md": "home-lifestyle-gifts",
    "ba-023-textured-acrylic-handbag-vase.md": "home-lifestyle-gifts",
    "ba-024-large-acrylic-handbag-ice-bucket-beverage-tub.md": "home-lifestyle-gifts",

    # === Kitchen Gadgets (51) ===
    "dw-016-stainless-steel-oil-dispenser-glass-soy-sauce-vinegar-bottle.md": "kitchen-gadgets",
    "dw-017-oil-sprayer-cooking-oil-dispenser-mist-spray-bottle.md": "kitchen-gadgets",
    "dw-019-popsicle-mold-ice-cream-mold-frozen-treat-maker.md": "kitchen-gadgets",
    "dw-021-silicone-ice-cube-tray-sports-water-cup-insulated-bottle.md": "kitchen-gadgets",
    "dw-022-6-side-box-grater-stainless-steel-shredder-slicer.md": "kitchen-gadgets",
    "dw-023-4-side-box-grater-stainless-steel-shredder-collection-base.md": "kitchen-gadgets",
    "dw-024-wooden-knob-box-grater-stainless-steel-vintage-shredder.md": "kitchen-gadgets",
    "dw-025-all-stainless-steel-box-grater-6-side-professional-shredder.md": "kitchen-gadgets",
    "dw-026-black-handle-6-side-box-grater-ergonomic-shredder.md": "kitchen-gadgets",
    "dw-027-large-arc-handle-4-side-box-grater-ergonomic-shredder.md": "kitchen-gadgets",
    "dw-028-stainless-steel-wood-handle-kitchen-spatula-turner-slotted-spoon.md": "kitchen-gadgets",
    "dw-029-stainless-steel-black-handle-kitchen-spatula-turner-slotted.md": "kitchen-gadgets",
    "dw-030-stainless-steel-chef-knife-set-kitchen-knife-block.md": "kitchen-gadgets",
    "dw-031-kitchen-scissors-shears-multicolor-handle-cutting-tool.md": "kitchen-gadgets",
    "dw-032-stainless-steel-manual-whisk-egg-beater-mixing-whip.md": "kitchen-gadgets",
    "dw-033-usb-rechargeable-electric-mixer-hand-blender-egg-beater.md": "kitchen-gadgets",
    "dw-034-aluminum-manual-lemon-squeezer-citrus-juicer-press.md": "kitchen-gadgets",
    "dw-035-aluminum-manual-lemon-squeezer-green-handle-wood-grip.md": "kitchen-gadgets",
    "dw-036-two-tone-orange-yellow-aluminum-manual-lemon-squeezer.md": "kitchen-gadgets",
    "dw-037-stainless-steel-manual-lemon-squeezer-natural-metal.md": "kitchen-gadgets",
    "dw-038-compact-aluminum-lime-squeezer-mini-citrus-press.md": "kitchen-gadgets",
    "dw-039-stainless-steel-garlic-press-crusher-heavy-duty.md": "kitchen-gadgets",
    "kg-001-stainless-steel-garlic-press.md": "kitchen-gadgets",
    "kg-002-stainless-steel-french-fry-cutter.md": "kitchen-gadgets",
    "kg-002-stainless-steel-vegetable-peeler.md": "kitchen-gadgets",
    "kg-003-manual-can-opener-wholesale.md": "kitchen-gadgets",
    "kg-003-multi-function-vegetable-slicer.md": "kitchen-gadgets",
    "kg-004-fruit-cutter.md": "kitchen-gadgets",
    "kg-005-electric-salt-pepper-grinder-set.md": "kitchen-gadgets",
    "kg-012-stainless-steel-grater-shredder-set.md": "kitchen-gadgets",
    "kg-013-stainless-steel-whisk-set.md": "kitchen-gadgets",
    "kg-014-stainless-steel-ladle-slotted-spoon-serving-set.md": "kitchen-gadgets",
    "kg-015-stainless-steel-measuring-spoon-cup-set.md": "kitchen-gadgets",
    "kg-016-stainless-steel-kitchen-specialty-tools-set.md": "kitchen-gadgets",
    "kg-017-grey-handle-stainless-steel-cooking-spoon-set.md": "kitchen-gadgets",
    "kg-018-stainless-steel-grater-whisk-sifter-prep-tool-set.md": "kitchen-gadgets",
    "kg-019-stainless-steel-floral-trivet-coaster-set.md": "kitchen-gadgets",
    "kg-021-kitchen-multi-function-scissors-shears-set.md": "kitchen-gadgets",
    "kg-040-stainless-steel-measuring-cup-handle-brushed-kitchen-wholesale.md": "kitchen-gadgets",
    "kg-041-stainless-steel-funnel-set-kitchen-strainer-conical-wholesale.md": "kitchen-gadgets",
    "kg-042-stainless-steel-mesh-strainer-skimmer-ladle-kitchen-wholesale.md": "kitchen-gadgets",
    "kg-043-stainless-steel-salt-pepper-shaker-spice-dispenser-wholesale.md": "kitchen-gadgets",
    "kg-044-stainless-steel-spice-canister-storage-jar-window-kitchen-wholesale.md": "kitchen-gadgets",
    "kg-045-stainless-steel-utensil-holder-caddy-perforated-kitchen-organizer-wholesale.md": "kitchen-gadgets",
    "kg-046-stainless-steel-long-handle-soup-ladle-serving-wholesale.md": "kitchen-gadgets",
    "kg-047-stainless-steel-skimmer-strainer-ladle-kitchen-wholesale.md": "kitchen-gadgets",
    "kg-048-stainless-steel-measuring-cup-spoon-set-kitchen-wholesale.md": "kitchen-gadgets",
    "kg-050-stainless-steel-pvd-gold-kitchen-utensil-set-luxury-wholesale.md": "kitchen-gadgets",
    "kg-051-stainless-steel-sauce-ladle-gravy-spoon-oval-kitchen-wholesale.md": "kitchen-gadgets",
    "so-005-stainless-steel-mixing-bowl-set-with-gold-pvd-cocktail-shaker.md": "kitchen-gadgets",
    "so-022-metal-wire-trivet-hot-pad-cutout-pattern-black-gold-wholesale.md": "kitchen-gadgets",

    # === Outdoor & Camping Gear (12) ===
    "kg-022-desktop-single-burner-gas-stove-camping-cooker.md": "outdoor-camping",
    "kg-023-portable-butane-camping-stove-cartridge-cooker.md": "outdoor-camping",
    "kg-026-cast-iron-burger-press-wood-handle-squeezer.md": "outdoor-camping",
    "kg-027-electric-bbq-grill-cleaning-brush-rotating.md": "outdoor-camping",
    "kg-032-stainless-steel-rectangular-bbq-grill-mesh-wood-handle-wholesale.md": "outdoor-camping",
    "kg-033-stainless-steel-square-bbq-grill-basket-wood-handle-set-wholesale.md": "outdoor-camping",
    "kg-034-green-round-metal-kerosene-camping-stove-wholesale.md": "outdoor-camping",
    "kg-035-green-square-metal-kerosene-field-stove-wholesale.md": "outdoor-camping",
    "kg-036-butane-cooking-torch-baking-flame-gun-multicolor-wholesale.md": "outdoor-camping",
    "kg-037-portable-single-burner-gas-stove-camping-cooker-colorful-wholesale.md": "outdoor-camping",
    "kg-038-stainless-steel-electric-hot-plate-cooker-single-burner-wholesale.md": "outdoor-camping",
    "kg-039-electric-charcoal-starter-hot-plate-black-camping-cooker-wholesale.md": "outdoor-camping",

    # === Storage & Organization (21) ===
    "dw-020-lunch-box-bento-box-food-container-meal-prep.md": "storage-organization",
    "so-001-glass-spice-jar-set-12pcs-with-stand.md": "storage-organization",
    "so-002-glass-storage-canister-with-bamboo-wood-lid.md": "storage-organization",
    "so-003-marble-pattern-glass-canister-with-gold-lid.md": "storage-organization",
    "so-004-stainless-steel-kitchen-canister-set.md": "storage-organization",
    "so-006-glass-food-storage-container-with-colored-lid.md": "storage-organization",
    "so-007-stainless-steel-square-sensor-trash-can.md": "storage-organization",
    "so-008-stainless-steel-round-step-trash-can.md": "storage-organization",
    "so-009-ceramic-kitchen-canister-set-bow-handle.md": "storage-organization",
    "so-010-ceramic-canister-wooden-lid-gold-knob.md": "storage-organization",
    "so-011-pp-woven-two-tone-handle-basket-fruit-storage.md": "storage-organization",
    "so-012-pp-woven-wave-edge-bowl-basket-decorative-serving.md": "storage-organization",
    "so-013-pp-woven-wood-handle-tray-serving-basket.md": "storage-organization",
    "so-014-fabric-lined-woven-basket-removable-liner-pattern.md": "storage-organization",
    "so-015-natural-rattan-woven-storage-basket-clothes-hamper.md": "storage-organization",
    "so-016-pp-woven-oval-bread-basket-boat-shape-serving.md": "storage-organization",
    "so-017-metal-wire-wall-mount-coat-hook-rack-wood-knob-wholesale.md": "storage-organization",
    "so-018-metal-wire-oval-scalloped-edge-storage-basket-black-gold-wholesale.md": "storage-organization",
    "so-019-metal-wire-tulip-petal-flower-storage-basket-black-gold-wholesale.md": "storage-organization",
    "so-020-metal-wire-cylindrical-pencil-holder-utensil-organizer-black-gold-wholesale.md": "storage-organization",
    "so-021-metal-wire-decorative-cutout-lace-storage-cylinder-black-gold-wholesale.md": "storage-organization",

    # === Tableware & Dining (13) ===
    "ba-053-gold-rim-glass-dessert-bowl-salad-bowl-petal-shape-wholesale.md": "tableware-dining",
    "ba-054-heart-shaped-flower-shaped-glass-dish-dessert-plate-set-wholesale.md": "tableware-dining",
    "dw-001-floral-porcelain-dinner-plate-set.md": "tableware-dining",
    "dw-002-pierced-reticulated-porcelain-plate-set.md": "tableware-dining",
    "dw-003-covered-ceramic-casserole-serving-dish-set.md": "tableware-dining",
    "dw-004-ceramic-cup-saucer-gift-set.md": "tableware-dining",
    "dw-005-inspirational-text-mug-cup-set.md": "tableware-dining",
    "dw-006-floral-heart-pattern-cup-saucer-set.md": "tableware-dining",
    "dw-007-geometric-checkered-cup-saucer-set.md": "tableware-dining",
    "dw-008-color-glazed-text-bowl-set.md": "tableware-dining",
    "dw-009-blue-white-traditional-cup-saucer-set.md": "tableware-dining",
    "kg-010-silicone-kids-animal-dining-set.md": "tableware-dining",
    "kg-011-silicone-divided-kids-plate-set.md": "tableware-dining",
}


def replace_categories_field(content, new_category):
    """
    在 YAML front matter 中替换 categories 字段。
    仅修改 categories 字段，保留文件其他所有内容不变。

    支持两种 YAML 数组格式：
      1. 行内格式: categories: ["item1", "item2"]
      2. 块格式:
         categories:
           - "item1"
           - "item2"

    返回: (new_content, changed, reason)
    """
    # 检测行尾符（Windows \r\n 或 Unix \n）
    if '\r\n' in content:
        le = '\r\n'
    else:
        le = '\n'

    lines = content.split(le)

    # 定位 front matter（第一个 --- 和第二个 --- 之间）
    if not lines or lines[0].strip() != '---':
        return content, False, "no front matter opening ---"

    fm_end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            fm_end_idx = i
            break

    if fm_end_idx is None:
        return content, False, "no front matter closing ---"

    # 逐行处理 front matter，只动 categories 字段
    fm_lines = lines[1:fm_end_idx]
    new_fm_lines = []
    i = 0
    found = False

    while i < len(fm_lines):
        line = fm_lines[i]
        stripped = line.lstrip()

        # 匹配 categories: 字段（精确匹配，不会匹配 categories_xxx:）
        if stripped.startswith('categories:'):
            found = True
            indent = line[:len(line) - len(line.lstrip())]
            rest = stripped[11:].strip()  # "categories:" 之后的内容

            if rest.startswith('['):
                # 行内格式: categories: ["item1", "item2"]
                new_fm_lines.append(f'{indent}categories: ["{new_category}"]')
                i += 1
            elif rest == '':
                # 块格式: categories:\n  - "item1"\n  - "item2"
                new_fm_lines.append(f'{indent}categories: ["{new_category}"]')
                i += 1
                # 跳过所有后续的列表项（以缩进的 - 开头的行）
                while i < len(fm_lines) and re.match(r'^\s+-\s', fm_lines[i]):
                    i += 1
            else:
                # categories: some_value（非数组单值格式，极少见）
                new_fm_lines.append(f'{indent}categories: ["{new_category}"]')
                i += 1
        else:
            # 非 categories 行，原样保留
            new_fm_lines.append(line)
            i += 1

    if not found:
        return content, False, "no categories field found"

    # 重新组装完整文件
    new_lines = [lines[0]] + new_fm_lines + lines[fm_end_idx:]
    new_content = le.join(new_lines)

    return new_content, True, "ok"


def main():
    print("=" * 60)
    print("  批量修改产品 categories 字段")
    print("  仅修改 categories，不改动其他任何内容")
    print("=" * 60)

    if not os.path.isdir(PRODUCTS_DIR):
        print(f"\n[错误] 产品目录不存在: {PRODUCTS_DIR}")
        print("请确认脚本位于仓库根目录下（与 content/ 同级）")
        sys.exit(1)

    # 收集所有 .md 文件
    md_files = sorted([f for f in os.listdir(PRODUCTS_DIR) if f.endswith('.md')])
    print(f"\n共找到 {len(md_files)} 个 MD 文件\n")

    modified = 0
    skipped = 0
    not_in_mapping = []
    errors = []

    for filename in md_files:
        filepath = os.path.join(PRODUCTS_DIR, filename)

        # 读取文件
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"  [错误] {filename} - 读取失败: {e}")
            errors.append(filename)
            continue

        # 确定新类目
        if filename in CATEGORY_MAPPING:
            new_category = CATEGORY_MAPPING[filename]
        else:
            # 不在映射表中的文件 → 设为 "other"
            new_category = "other"
            not_in_mapping.append(filename)

        # 替换 categories 字段
        new_content, changed, reason = replace_categories_field(content, new_category)

        if not changed:
            if reason == "no categories field found":
                # 没有 categories 字段的文件（如 _index.md），跳过不处理
                skipped += 1
                continue
            else:
                print(f"  [跳过] {filename} - {reason}")
                skipped += 1
                continue

        # 检查是否有实际变化（避免无意义写入）
        if content == new_content:
            print(f"  [无变化] {filename} - categories 已是 [{new_category}]")
            skipped += 1
            continue

        # 写回文件
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
        except Exception as e:
            print(f"  [错误] {filename} - 写入失败: {e}")
            errors.append(filename)
            continue

        tag = "[其他]" if filename not in CATEGORY_MAPPING else "[修改]"
        print(f"  {tag} {filename}")
        print(f"         -> categories: [\"{new_category}\"]")
        modified += 1

    # 汇总报告
    print("\n" + "=" * 60)
    print(f"  完成！")
    print(f"  已修改: {modified} 个文件")
    print(f"  已跳过: {skipped} 个文件")
    if errors:
        print(f"  错误:   {len(errors)} 个文件")
        for e in errors:
            print(f"    - {e}")
    print("=" * 60)

    if not_in_mapping:
        print(f"\n以下 {len(not_in_mapping)} 个文件不在分类映射表中，已设为 [other]:")
        for f in not_in_mapping:
            print(f"  - {f}")
        print("\n请检查以上文件是否需要手动归类。")


if __name__ == "__main__":
    main()
