# Pin'Log

An open notebook for learning notes, questions, observations, and life records. Published at <https://pinqian77.github.io/pin-log/> with Jekyll and GitHub Pages.

The design uses warm paper surfaces, serif headings, a restrained red accent, reusable article components, and optional interactive concept diagrams. English is the first-visit default. Readers can switch to Chinese; their choice is remembered in the browser.

## Writing a new note

Add a Markdown file to `_posts/` named `YYYY-MM-DD-your-title.md`. Only `layout`, `title`, `date`, and `tags` are needed. All notes appear on the homepage, in the archive, and under their tags automatically. New subjects do not require template changes.

```yaml
---
layout: post
title: "An idea worth keeping"
title_zh: "一个值得留下的想法"
date: 2026-10-12 09:00:00
tags: [reading, life]
summary: "A short introduction to the note."
summary_zh: "这篇笔记的简短介绍。"
---
```

Write the body below the front matter. Put `<!--more-->` after an opening paragraph if you prefer automatic excerpts instead of `summary`.

Optional fields:

- `featured: true` selects the homepage lead note. Remove this field from the previously selected note when choosing another. Without a selection, the latest note is featured.
- `display_title` and `display_title_zh` provide a shorter homepage headline without changing the article title.
- `takeaway` and `takeaway_zh` add the article's takeaway block.
- `visual` selects a reusable cover: `policy`, `logging`, `locking`, `timestamp`, or `theory`. Omit it for the general notebook cover. `policy` and `logging` also enable a concept walkthrough.
- `translation_zh: translations/your-note.md` points to a Chinese body in `_includes/translations/`. Without a translation, the Chinese view clearly identifies the article as English and preserves access to its original text.

Add optional English/Chinese topic labels and descriptions to `_data/topics.yml`. Unknown tags are still displayed and listed automatically. Existing article URLs and legacy tag pages are retained.

## Local build

```sh
bundle install
bundle exec jekyll build
bundle exec jekyll serve
```

This repository originally used the theme from [Lilian Weng's lil-log](https://github.com/lilianweng/lil-log). Original articles and image assets have been retained; the notebook interface and bilingual additions are maintained here.

