#!/usr/bin/env bash
set -e

if [ -z "$1" ]; then
  echo "用法: bash scripts/init_git_repo.sh git@github.com:你的用户名/你的仓库名.git"
  exit 1
fi

git init
git branch -M main
git add .
git commit -m "Initial Hugo GitHub Pages site"
git remote add origin "$1"
git push -u origin main

echo "已推送到 GitHub。接下来到仓库 Settings → Pages，把 Source 改为 GitHub Actions。"
