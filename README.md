# Hugo 第一分公司网站基础包

这套基础包把前面确定的第一分公司方案改成 Hugo 版，适合长期维护 500+ 产品页，并可复制给第二、第三分公司。

## 已确定的网站定位

- 网站类型：B2B Online Wholesale Showroom
- 核心定位：Home & Kitchen Wholesale Showroom from Yiwu China
- 首批类目：Kitchen Gadgets、Storage & Organization、Cleaning Tools、Bathroom Accessories、Home Lifestyle Gifts
- 部署方式：Hugo + GitHub Pages + GitHub Actions
- 内容来源：产品 CSV/XLSX → Hugo Markdown → 静态网站

## 日常编辑位置

| 你要改什么 | 修改哪里 |
|---|---|
| 公司名、电话、邮箱、地址 | `data/company.yaml` |
| 类目名称和说明 | `data/categories.yaml` |
| 页脚链接和贸易条款 | `data/footer.yaml` |
| 首页内容 | `content/_index.md` 和 `layouts/index.html` |
| 产品内容 | `content/products/*.md` |
| 产品页样式 | `layouts/products/single.html` |
| 全站样式 | `static/css/main.css` |
| GitHub Pages 自动部署 | `.github/workflows/hugo.yaml` |

## 从 CSV 批量生成产品页

```bash
python scripts/csv_to_hugo_markdown.py products.csv content/products/
```

生成后的产品会自动进入 `/products/` 列表页，并按 `categories` 字段进入对应类目页。

## 本地预览

```bash
hugo server -D
```

然后打开 `http://localhost:1313`。

## GitHub Pages 部署

1. 把整个项目推送到 GitHub 仓库。
2. 打开仓库 `Settings` → `Pages`。
3. Source 选择 `GitHub Actions`。
4. 推送到 `main` 分支后，Actions 会自动构建并发布。

## 后续统一管理原则

产品页只写产品内容，公共导航、页脚、联系方式、类目说明和样式都集中维护。新增产品不改导航，新增类目只改 `data/categories.yaml`，公司信息只改 `data/company.yaml`。


## 万能 CSV 到 Hugo frontmatter 的完整映射

本基础包已经加入完整映射标准：

- `data/frontmatter_schema.yaml`：机器可读字段映射
- `scripts/csv_to_hugo_markdown.py`：按完整映射规则生成产品 Markdown
- `hugo-frontmatter-mapping-standard.xlsx`：人工查看和维护的字段映射表

CSV 转换命令：

```bash
python scripts/csv_to_hugo_markdown.py products.csv content/products/
```

转换后，公开字段用于产品页、类目页、SEO 和 AI/GEO；供应商、成本、质量备注和内部备注会保留在 frontmatter 中，但默认模板不显示。
