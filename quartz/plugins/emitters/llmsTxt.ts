import { FullSlug, joinSegments, simplifySlug } from "../../util/path"
import { QuartzEmitterPlugin } from "../types"
import { write } from "./helpers"

// Generates llms.txt (a short site index) and llms-full.txt (full page text)
// per the llms.txt convention (https://llmstxt.org/), so the site is
// machine-readable without needing to scrape and render every HTML page.
export const LlmsTxt: QuartzEmitterPlugin = () => ({
  name: "LlmsTxt",
  async *emit(ctx, content) {
    const cfg = ctx.cfg.configuration
    const base = cfg.baseUrl ?? ""

    type Entry = {
      slug: FullSlug
      title: string
      description: string
      text: string
    }

    const entries: Entry[] = []
    for (const [, file] of content) {
      const slug = file.data.slug
      if (!slug) continue
      if (!file.data.text || file.data.text === "") continue
      entries.push({
        slug,
        title: file.data.frontmatter?.title ?? slug,
        description: file.data.description ?? "",
        text: file.data.text,
      })
    }

    entries.sort((a, b) => a.slug.localeCompare(b.slug))

    const urlFor = (slug: FullSlug) => `https://${joinSegments(base, encodeURI(simplifySlug(slug)))}`

    const lines: string[] = []
    lines.push(`# ${cfg.pageTitle}`)
    lines.push("")
    lines.push(
      "> A personal AI/ML, robotics, and VLSI research lab and technical notebook — projects, research, experiments, and interlinked notes.",
    )
    lines.push("")
    lines.push("## Pages")
    lines.push("")
    for (const e of entries) {
      const desc = e.description ? ` — ${e.description}` : ""
      lines.push(`- [${e.title}](${urlFor(e.slug)})${desc}`)
    }
    lines.push("")

    yield write({
      ctx,
      content: lines.join("\n"),
      slug: "llms" as FullSlug,
      ext: ".txt",
    })

    const fullLines: string[] = []
    fullLines.push(`# ${cfg.pageTitle}`)
    fullLines.push("")
    for (const e of entries) {
      fullLines.push(`---`)
      fullLines.push("")
      fullLines.push(`## ${e.title}`)
      fullLines.push("")
      fullLines.push(`URL: ${urlFor(e.slug)}`)
      fullLines.push("")
      fullLines.push(e.text)
      fullLines.push("")
    }

    yield write({
      ctx,
      content: fullLines.join("\n"),
      slug: "llms-full" as FullSlug,
      ext: ".txt",
    })
  },
})
