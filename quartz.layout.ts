import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"

// Top-level Explorer order follows the site's information architecture
// (About -> Work -> Knowledge) instead of plain alphabetical.
//
// IMPORTANT: Quartz serializes sortFn/filterFn via Function.prototype.toString()
// and re-evaluates them client-side, so they cannot close over any variable
// declared outside the function body (e.g. a top-level const) — every value
// they use must be inlined inside the function itself.
const explorerOptions = {
  title: "Explorer",
  filterFn: (node: { slugSegment: string }) =>
    node.slugSegment !== "tags" && node.slugSegment !== "attachments",
  sortFn: (
    a: { isFolder: boolean; slugSegment: string; displayName: string },
    b: { isFolder: boolean; slugSegment: string; displayName: string },
  ) => {
    const topLevelOrder = ["about", "work", "notes"]
    if (a.isFolder && b.isFolder) {
      const ai = topLevelOrder.indexOf(a.slugSegment)
      const bi = topLevelOrder.indexOf(b.slugSegment)
      if (ai !== -1 || bi !== -1) {
        if (ai === -1) return 1
        if (bi === -1) return -1
        return ai - bi
      }
      return a.displayName.localeCompare(b.displayName, undefined, {
        numeric: true,
        sensitivity: "base",
      })
    }
    if (a.isFolder !== b.isFolder) return a.isFolder ? -1 : 1
    return a.displayName.localeCompare(b.displayName, undefined, {
      numeric: true,
      sensitivity: "base",
    })
  },
}

// components shared across all pages
export const sharedPageComponents: SharedLayout = {
  head: Component.Head(),
  header: [],
  afterBody: [
    Component.ConditionalRender({
      component: Component.Graph({
        localGraph: {
          depth: -1,
          scale: 0.9,
          repelForce: 0.8,
          centerForce: 0.15,
          linkDistance: 40,
        },
      }),
      condition: (page) => page.fileData.slug === "graph",
    }),
  ],
  footer: Component.Footer({
    links: {
      GitHub: "https://github.com/JubayerONROB",
      LinkedIn: "https://linkedin.com/in/a-j-a-jubayer-talukder",
      Email: "mailto:ajajubayertalukder@gmail.com",
    },
  }),
}

// components for pages that display a single page (e.g. a single note)
export const defaultContentPageLayout: PageLayout = {
  beforeBody: [
    Component.ConditionalRender({
      component: Component.Breadcrumbs(),
      condition: (page) => page.fileData.slug !== "index",
    }),
    Component.ConditionalRender({
      component: Component.ArticleTitle(),
      condition: (page) => page.fileData.slug !== "index",
    }),
    Component.ContentMeta(),
    Component.TagList(),
  ],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        {
          Component: Component.Search(),
          grow: true,
        },
        { Component: Component.Darkmode() },
        { Component: Component.ReaderMode() },
      ],
    }),
    Component.Explorer(explorerOptions),
  ],
  right: [
    Component.Graph({
      globalGraph: {
        repelForce: 0.8,
        centerForce: 0.15,
        linkDistance: 40,
      },
    }),
    Component.DesktopOnly(Component.TableOfContents()),
    Component.Backlinks(),
  ],
}

// components for pages that display lists of pages  (e.g. tags or folders)
export const defaultListPageLayout: PageLayout = {
  beforeBody: [Component.Breadcrumbs(), Component.ArticleTitle(), Component.ContentMeta()],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        {
          Component: Component.Search(),
          grow: true,
        },
        { Component: Component.Darkmode() },
      ],
    }),
    Component.Explorer(explorerOptions),
  ],
  right: [],
}
