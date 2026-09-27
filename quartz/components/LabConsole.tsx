import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import style from "./styles/labConsole.scss"

function countBySlugPrefix(allFiles: QuartzComponentProps["allFiles"], prefix: string): number {
  return allFiles.filter((f) => {
    const slug = f.slug as string | undefined
    return slug?.startsWith(prefix) && !slug.endsWith("/index") && slug !== prefix.replace(/\/$/, "")
  }).length
}

const LabConsole: QuartzComponent = ({ fileData, allFiles, displayClass }: QuartzComponentProps) => {
  if (fileData.slug !== "index") {
    return null
  }

  const projectCount = countBySlugPrefix(allFiles, "work/projects/")
  const researchCount = countBySlugPrefix(allFiles, "work/research/")
  const noteCount = countBySlugPrefix(allFiles, "notes/")

  const tagCounts = new Map<string, number>()
  for (const file of allFiles) {
    const tags = (file.frontmatter?.tags ?? []) as string[]
    for (const tag of tags) {
      tagCounts.set(tag, (tagCounts.get(tag) ?? 0) + 1)
    }
  }
  const topTags = [...tagCounts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6)

  return (
    <div class={`lab-console ${displayClass ?? ""}`}>
      <div class="lab-console-header">
        <span class="lab-console-dot" />
        A. J. A. JUBAYER TALUKDER // STATUS
      </div>
      <div class="lab-console-body">
        <ul class="lab-console-stats">
          <li>
            <span class="lab-console-label">PROJECTS</span>
            <span class="lab-console-value">{String(projectCount).padStart(2, "0")}</span>
          </li>
          <li>
            <span class="lab-console-label">RESEARCH</span>
            <span class="lab-console-value">{String(researchCount).padStart(2, "0")}</span>
          </li>
          <li>
            <span class="lab-console-label">NOTES</span>
            <span class="lab-console-value">{String(noteCount).padStart(2, "0")}</span>
          </li>
        </ul>
        <ul class="lab-console-tags">
          {topTags.map(([tag, count]) => (
            <li>
              <a href={`/tags/${tag}`} class="internal">
                {tag}
              </a>
              <span class="lab-console-tag-count">{count}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

LabConsole.css = style

export default (() => LabConsole) satisfies QuartzComponentConstructor
