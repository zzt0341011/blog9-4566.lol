import os
import re
import yaml
from pypinyin import lazy_pinyin

DATA_FILE = "data/webstack.yml"
OUTPUT_DIR = "content/sites"
SLUG_FILE = "data/site-slugs.yml"

def make_slug(title):
    value = "-".join(lazy_pinyin(str(title).strip().lower()))
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")

def load_yaml_documents():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data=[]
        for doc in yaml.safe_load_all(f):
            if isinstance(doc,list): data.extend(doc)
            elif isinstance(doc,dict): data.append(doc)
        return data

def flatten_links(data):
    sites=[]
    for category in data:
        if not isinstance(category,dict): continue
        for link in category.get("links",[]):
            if isinstance(link,dict): sites.append(link)
        for sub in category.get("list",[]):
            if isinstance(sub,dict):
                for link in sub.get("links",[]):
                    if isinstance(link,dict): sites.append(link)
    return sites

def clean(v):
    return str(v or "").replace('"','\\"').replace("\r"," ").replace("\n"," ").strip()

def create_markdown(site):
    title=str(site.get("title","")).strip()
    if not title: return None
    slug=str(site.get("slug","")).strip().lower() or make_slug(title)
    if not slug: return None
    description=clean(site.get("description",""))
    website=clean(site.get("url",""))
    logo=clean(site.get("logo",""))
    keywords=[title,f"{title}官网",f"{title}官方网站",f"{title}介绍",f"{title}是什么"]
    content=f'''---
title: "{clean(title)}"
description: "{description}"
keywords:
'''
    for k in keywords: content += f'  - "{clean(k)}"\n'
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
- 访问 {title} 官方网站

## {title} 适合哪些人？

{title} 适合需要相关服务、工具、内容或资源的用户。

## {title} 的主要特点

{title} 提供了与其服务领域相关的内容和功能。

第一次使用时，建议先访问官方网站，了解具体服务、使用方式以及最新信息。

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

点击“立即访问 {title} 官网”即可进入官方网站。

### {title} 是否值得收藏？

如果你经常需要使用 {title} 提供的服务，可以将其加入浏览器书签。
'''
    os.makedirs(OUTPUT_DIR,exist_ok=True)
    with open(os.path.join(OUTPUT_DIR,slug+'.md'),'w',encoding='utf-8') as f: f.write(content)
    print('生成：'+os.path.join(OUTPUT_DIR,slug+'.md'))
    return slug

def main():
    print('读取：',DATA_FILE)
    data=load_yaml_documents(); sites=flatten_links(data)
    print(f'发现网站：{len(sites)} 个')
    seen=set(); mapping={}; success=skipped=0
    for site in sites:
        title=str(site.get('title','')).strip()
        slug=str(site.get('slug','')).strip().lower() or make_slug(title)
        if not slug or slug in seen:
            skipped+=1; continue
        seen.add(slug); mapping[title]=slug
        if create_markdown(site): success+=1
        else: skipped+=1
    os.makedirs('data',exist_ok=True)
    with open(SLUG_FILE,'w',encoding='utf-8') as f:
        yaml.safe_dump(mapping,f,allow_unicode=True,sort_keys=False)
    print('='*50); print('详情页生成完成'); print('='*50)
    print(f'成功：{success}'); print(f'跳过：{skipped}'); print(f'Slug 映射：{SLUG_FILE}')

if __name__=='__main__': main()
