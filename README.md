# jubayeronrob.github.io

Personal digital-lab portfolio, built with [Quartz v4](https://quartz.jzhao.xyz) — an open-source digital-garden static site generator (MIT licensed; the same engine used by Plastic Labs' website). No content, branding, or design assets were copied from any other site.

## Editing content

All content lives under `content/` as plain Markdown files:

- `content/index.md` — homepage
- `content/about.md`, `content/resume.md`
- `content/research/` — research write-ups
- `content/projects/` — project entries
- `content/notes/` — short interlinked technical notes
- `content/attachments/cv.pdf` — resume PDF

To add a new project or note, just add a new `.md` file in the relevant folder (with frontmatter `title`, `date`, `tags`) and commit — no code changes required. Wikilinks (`[[projects/foo|Label]]`) create backlinks and graph edges automatically.

## Local development

```bash
npm ci
npx quartz build --serve
```

## Deployment

Pushing to `main` triggers `.github/workflows/deploy.yml`, which builds the site and publishes it to GitHub Pages automatically. Make sure the repo's Settings → Pages → Source is set to "GitHub Actions".

## Configuration

- `quartz.config.ts` — site title, theme colors, plugins
- `quartz.layout.ts` — sidebar/explorer, page layout, footer links
