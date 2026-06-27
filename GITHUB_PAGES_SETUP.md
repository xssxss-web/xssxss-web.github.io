# GitHub Pages 建站说明

这份说明用于把当前 Hugo 第一分公司网站发布到 GitHub Pages。

## 第一步：创建 GitHub 仓库

登录 GitHub 后，新建一个仓库。建议仓库名使用：

```text
hugo-first-branch
```

如果你以后要绑定独立域名，仓库名可以随意；如果你暂时不用独立域名，网站地址通常会是：

```text
https://你的GitHub用户名.github.io/hugo-first-branch/
```

## 第二步：上传项目文件

把 `hugo-first-branch-blueprint` 文件夹里的所有内容上传到 GitHub 仓库根目录。

注意：上传后，仓库根目录应该能直接看到这些文件和目录：

```text
hugo.yaml
content/
data/
layouts/
static/
scripts/
.github/
README.md
```

不要把整个 `hugo-first-branch-blueprint` 文件夹作为子目录上传，否则 GitHub Actions 找不到 `hugo.yaml`。

## 第三步：开启 GitHub Pages

进入仓库页面：

```text
Settings → Pages
```

在 `Build and deployment` 里：

```text
Source: GitHub Actions
```

选择后不需要额外保存。

## 第四步：触发自动部署

项目里已经包含：

```text
.github/workflows/hugo.yaml
```

每次你把文件推送到 `main` 分支，GitHub Actions 会自动：

```text
安装 Hugo → 构建网站 → 发布到 GitHub Pages
```

部署过程可以在仓库的 `Actions` 页面查看。

## 第五步：查看网站

部署成功后，进入：

```text
Settings → Pages
```

页面会显示正式访问地址。

也可以在 `Actions` 里点击最近一次成功的部署记录查看网址。

## 后续日常更新

新增产品时：

```bash
python scripts/csv_to_hugo_markdown.py products.csv content/products/
git add .
git commit -m "Add new products"
git push
```

GitHub Pages 会自动重新构建并发布。

## 常见问题

### 页面打开后样式丢失

通常是项目没有放在仓库根目录，或者 GitHub Pages 还没部署完成。先确认仓库根目录有 `hugo.yaml`。

### Actions 构建失败

进入 `Actions` 页面，点开失败记录，看红色报错。常见原因是 frontmatter YAML 格式错误，例如引号没有闭合、冒号后缺少空格。

### 想绑定自己的域名

后面可以在 `Settings → Pages → Custom domain` 里绑定域名。绑定前先确认 DNS 已经配置到 GitHub Pages。
