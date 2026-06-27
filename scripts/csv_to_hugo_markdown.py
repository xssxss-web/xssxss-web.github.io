import csv, re, sys
from pathlib import Path
from datetime import date

NUMERIC_FIELDS = {
    "weight_g", "carton_qty_pcs", "carton_gw_kg", "carton_nw_kg",
    "moq_pcs", "price_min_usd", "price_max_usd", "sample_fee_usd",
    "source_cost_rmb"
}

BOOL_TRUE = {"yes", "true", "1", "y", "是", "支持", "available"}
BOOL_FALSE = {"no", "false", "0", "n", "否", "不支持", "not available"}

def slugify(s):
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    return re.sub(r"[\s-]+", "-", s).strip("-")

def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'

def split_list(v):
    if not v:
        return []
    parts = re.split(r"[,|;；，]", str(v))
    return [x.strip() for x in parts if x.strip()]

def yaml_list(v):
    return "[" + ", ".join(q(x) for x in split_list(v)) + "]"

def to_bool(v):
    s = str(v or "").strip().lower()
    if s in BOOL_TRUE:
        return True
    if s in BOOL_FALSE:
        return False
    return None

def add(lines, key, value, numeric=False):
    if value is None or str(value).strip() == "":
        return
    v = str(value).strip()
    if numeric:
        try:
            n = float(v)
            if n.is_integer():
                n = int(n)
            lines.append(f"{key}: {n}")
            return
        except ValueError:
            pass
    lines.append(f"{key}: {q(v)}")

def add_bool(lines, key, value):
    b = to_bool(value)
    if b is not None:
        lines.append(f"{key}: {'true' if b else 'false'}")

def add_block(lines, key, value):
    if value and str(value).strip():
        lines.append(f"{key}: |")
        for line in str(value).strip().splitlines():
            lines.append(f"  {line}")

def draft_from_status(status):
    s = str(status or "").strip().lower()
    return "false" if s in {"active", "published", "publish", "上线", "已发布"} else "true"

def build(row):
    sku = row.get("sku", "").strip()
    title = row.get("product_name_en", "").strip()
    if not sku or not title:
        return None, None

    slug = row.get("slug", "").strip() or slugify(title)
    category = slugify(row.get("category", ""))
    subcategory = slugify(row.get("subcategory", ""))
    status = row.get("product_status", "active").strip() or "active"

    lines = ["---"]
    add(lines, "title", title)
    add(lines, "slug", slug)
    add(lines, "sku", sku)
    add(lines, "branch_code", row.get("branch_code"))
    add(lines, "product_status", status)
    lines.append(f"draft: {draft_from_status(status)}")

    if category:
        lines.append(f"categories: [{q(category)}]")
    if subcategory:
        add(lines, "subcategory", subcategory)
    for csv_key, yaml_key in [("tags", "tags"), ("target_buyers", "buyers"), ("use_cases", "usecases")]:
        if row.get(csv_key):
            lines.append(f"{yaml_key}: {yaml_list(row.get(csv_key))}")

    add(lines, "summary", row.get("short_summary_en"))
    add(lines, "description", row.get("meta_description") or row.get("short_summary_en"))
    add(lines, "product_name_cn", row.get("product_name_cn"))
    add_block(lines, "long_description", row.get("description_en"))

    if row.get("selling_points"):
        lines.append(f"selling_points: {yaml_list(row.get('selling_points'))}")

    for key in [
        "material", "color_options", "size_cm", "weight_g", "packing",
        "carton_qty_pcs", "carton_size_cm", "carton_gw_kg", "carton_nw_kg",
        "moq_pcs", "price_min_usd", "price_max_usd", "sample_fee_usd"
    ]:
        add(lines, key, row.get(key), numeric=key in NUMERIC_FIELDS)

    add_bool(lines, "sample_available", row.get("sample_available"))
    add(lines, "lead_time_days", row.get("lead_time_days"))
    add_bool(lines, "mixed_order_supported", row.get("mixed_order_supported"))
    add(lines, "customization_options", row.get("customization_options"))
    add(lines, "certifications", row.get("certifications"))

    add(lines, "main_image", row.get("main_image"))
    if row.get("gallery_images"):
        lines.append("gallery_images:")
        for img in split_list(row.get("gallery_images")):
            lines.append(f"  - {q(img)}")
    add(lines, "image_alt", row.get("image_alt_en"))
    add(lines, "video_url", row.get("video_url"))

    add(lines, "meta_title", row.get("meta_title"))
    add(lines, "primary_keyword", row.get("primary_keyword"))
    if row.get("secondary_keywords"):
        lines.append(f"secondary_keywords: {yaml_list(row.get('secondary_keywords'))}")

    faq = []
    i = 1
    while True:
        qv = row.get(f"faq_{i}_q", "").strip()
        av = row.get(f"faq_{i}_a", "").strip()
        if not qv and not av and i > 4:
            break
        if qv and av:
            faq.append((qv, av))
        i += 1
    if faq:
        lines.append("faq:")
        for question, answer in faq:
            lines.append(f"  - question: {q(question)}")
            lines.append(f"    answer: {q(answer)}")

    if row.get("related_skus"):
        lines.append(f"related_skus: {yaml_list(row.get('related_skus'))}")

    supplier_keys = {
        "supplier_name": "name",
        "supplier_contact": "contact",
        "market_location": "market_location",
        "supplier_type": "type",
        "source_cost_rmb": "source_cost_rmb",
    }
    supplier = [(out, row.get(src, "")) for src, out in supplier_keys.items() if row.get(src, "").strip()]
    if supplier:
        lines.append("supplier:")
        for key, value in supplier:
            if key == "source_cost_rmb":
                try:
                    n = float(value)
                    if n.is_integer():
                        n = int(n)
                    lines.append(f"  {key}: {n}")
                except ValueError:
                    lines.append(f"  {key}: {q(value)}")
            else:
                lines.append(f"  {key}: {q(value)}")

    add(lines, "quality_notes", row.get("quality_notes"))
    add(lines, "risk_notes", row.get("risk_notes"))
    add(lines, "internal_notes", row.get("internal_notes"))
    add(lines, "last_updated", row.get("last_updated") or date.today().isoformat())
    lines.append("---\n")
    body = row.get("description_en", "").strip() or row.get("short_summary_en", "").strip()
    lines.append(body)
    return f"{sku.lower()}-{slug}.md", "\n".join(lines) + "\n"

def main():
    if len(sys.argv) < 3:
        print("用法: python scripts/csv_to_hugo_markdown.py products.csv content/products/")
        sys.exit(1)
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    count = 0
    with src.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            name, content = build(row)
            if name:
                (out / name).write_text(content, encoding="utf-8")
                count += 1
    print(f"已生成 {count} 个 Hugo 产品 Markdown 文件")

if __name__ == "__main__":
    main()
