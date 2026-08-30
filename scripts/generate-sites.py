import os
import re
import yaml
from pypinyin import lazy_pinyin


# =========================================================
# 配置
# =========================================================

DATA_FILE = "data/webstack.yml"
OUTPUT_DIR = "content/sites"
SLUG_FILE = "data/site-slugs.yml"


# =========================================================
# 生成 SEO slug
# =========================================================

def make_slug(title):

    value = str(title).strip().lower()

    # 中文转拼音
    value = "-".join(lazy_pinyin(value))

    # 非英文、数字全部转 -
    value = re.sub(r"[^a-z0-9]+", "-", value)

    # 清理连续 -
    value = re.sub(r"-+", "-", value)

    # 清理首尾 -
    value = value.strip("-")

    return value


# =========================================================
# 读取多个 YAML document
# =========================================================

def load_yaml_documents():

    with open(DATA_FILE, "r", encoding="utf-8") as f:

        documents = list(yaml.safe_load_all(f))

    all_data = []

    for document in documents:

        if not document:
            continue

        if isinstance(document, list):

            all_data.extend(document)

        elif isinstance(document, dict):

            all_data.append(document)

    return all_data


# =========================================================
# 提取所有网站
# =========================================================

def flatten_links(data):

    sites = []

    for category in data:

        if not isinstance(category, dict):
            continue

        # 一级分类
        for link in category.get("links", []):

            if isinstance(link, dict):

                sites.append(link)

        # 二级分类
        for subcategory in category.get("list", []):

            if not isinstance(subcategory, dict):
                continue

            for link in subcategory.get("links", []):

                if isinstance(link, dict):

                    sites.append(link)

    return sites


# =========================================================
# 清理文本
# =========================================================

def clean_text(value):

    if value is None:
        return ""

    value = str(value)

    value = value.replace("\r", " ")
    value = value.replace("\n", " ")
    value = value.replace('"', '\\"')

    return value.strip()


# =========================================================
# 生成详情页
# =========================================================

def create_markdown(site, slug):

    title = str(site.get("title", "")).strip()

    if not title:
        return False

    description = clean_text(
        site.get("description", "")
    )

    website = clean_text(
        site.get("url", "")
    )

    logo = clean_text(
        site.get("logo", "")
    )

    keywords = [
        title,
        f"{title}官网",
        f"{title}官方网站",
        f"{title}介绍",
        f"{title}是什么",
    ]

    content = f'''---
title: "{clean_text(title)}"
description: "{description}"
keywords:
'''

    for keyword in keywords:

        content += f'  - "{clean_text(keyword)}"\n'

    content += f'''website: "{website}"
logo: "{logo}"
slug: "{slug}"
---

# {title}

{description}

## {title} 是什么？

{title} 是一个值得收藏和使用的网站。

如果你正在寻找与 **{title}** 相关的服务、工具、内容或资源，可以通过本站了解相关信息。

## {title} 主要功能

- 了解 {title} 提供的服务
- 浏览 {title} 提供的内容
- 获取相关使用信息
- 了解网站主要特点
- 访问 {title} 官方网站

## {title} 适合哪些人？

{title} 适合需要相关服务、工具、内容或资源的用户。

如果你正在寻找类似的网站，可以先了解 {title} 的主要功能，再决定是否使用。

## {title} 的主要特点

{title} 提供了与其服务领域相关的内容和功能。

对于第一次使用的用户，建议先访问官方网站，了解具体服务、使用方式以及最新信息。

## {title} 官网

如果你想进一步了解 {title}，可以访问官方网站。

**[立即访问 {title} 官网]({website})**

## 常见问题

### {title} 是什么？

{title} 是一个提供相关服务、工具或内容的网站。

### {title} 官网在哪里？

{title} 的官方网站是：

{website}

### 如何访问 {title}？

你可以点击上方的“立即访问 {title} 官网”按钮进入官方网站。

### {title} 是否值得收藏？

如果你经常需要使用 {title} 提供的服务，那么可以将其加入浏览器书签，方便以后访问。

'''

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    filename = os.path.join(
        OUTPUT_DIR,
        slug + ".md"
    )

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(content)

    print(f"生成：{filename}")

    return True


# =========================================================
# 生成 slug 映射
# =========================================================

def save_slug_map(slug_map):

    os.makedirs(
        os.path.dirname(SLUG_FILE),
        exist_ok=True
    )

    with open(
        SLUG_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        yaml.safe_dump(
            slug_map,
            f,
            allow_unicode=True,
            sort_keys=False
        )

    print(f"Slug 映射：{SLUG_FILE}")


# =========================================================
# 主程序
# =========================================================

def main():

    print("读取：", DATA_FILE)

    data = load_yaml_documents()

    print(
        f"读取 YAML 分类：{len(data)} 个"
    )

    sites = flatten_links(data)

    print(
        f"发现网站：{len(sites)} 个"
    )

    success = 0
    skipped = 0

    seen_slugs = set()

    slug_map = {}

    for site in sites:

        title = str(
            site.get("title", "")
        ).strip()

        if not title:

            skipped += 1
            continue

        # -----------------------------------------
        # 优先使用 YAML 中手工指定 slug
        # -----------------------------------------

        slug = site.get("slug")

        if slug:

            slug = str(slug).strip().lower()

        else:

            slug = make_slug(title)

        if not slug:

            print(
                f"跳过：{title} —— 无法生成 slug"
            )

            skipped += 1
            continue

        # -----------------------------------------
        # 防止 slug 重复
        # -----------------------------------------

        original_slug = slug

        counter = 2

        while slug in seen_slugs:

            slug = f"{original_slug}-{counter}"

            counter += 1

        if slug != original_slug:

            print(
                f"Slug 重复：{title}"
                f" → {slug}"
            )

        seen_slugs.add(slug)

        # -----------------------------------------
        # 保存标题 → slug
        # -----------------------------------------

        slug_map[title] = slug

        # -----------------------------------------
        # 生成详情页
        # -----------------------------------------

        if create_markdown(
            site,
            slug
        ):

            success += 1

        else:

            skipped += 1

    # -----------------------------------------
    # 保存 slug 映射
    # -----------------------------------------

    save_slug_map(slug_map)

    print("")
    print("=" * 50)
    print("详情页生成完成")
    print("=" * 50)
    print(f"成功：{success}")
    print(f"跳过：{skipped}")
    print(f"输出目录：{OUTPUT_DIR}")
    print(f"Slug 映射：{SLUG_FILE}")


if __name__ == "__main__":

    main()