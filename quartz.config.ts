import { QuartzConfig } from "./quartz/cfg"
import * as Plugin from "./quartz/plugins"

/**
 * Quartz 4 Configuration
 *
 * See https://quartz.jzhao.xyz/configuration for more information.
 */
const config: QuartzConfig = {
  configuration: {
    pageTitle: "Jubayer — Digital Lab",
    pageTitleSuffix: "",
    enableSPA: true,
    enablePopovers: true,
    analytics: null,
    locale: "en-US",
    baseUrl: "jubayeronrob.github.io",
    ignorePatterns: ["private", "templates", ".obsidian"],
    defaultDateType: "created",
    theme: {
      fontOrigin: "googleFonts",
      cdnCaching: true,
      typography: {
        header: "Space Mono",
        body: "Roboto Mono",
        code: "Ubuntu Mono",
      },
      colors: {
        // A grayscale-canvas + mint-accent system in the spirit of a technical
        // lab notebook. Deliberately shifted from any single reference site's
        // exact values so the palette reads as its own identity.
        lightMode: {
          light: "#e6e6e4",
          lightgray: "#d4d4d2",
          gray: "#9a9a97",
          darkgray: "#4a4a48",
          dark: "#262624",
          secondary: "#128f68",
          tertiary: "#128f68",
          highlight: "rgba(184, 245, 214, 0.3)",
          textHighlight: "#b8f5d688",
        },
        darkMode: {
          light: "#1c1c1c",
          lightgray: "#333335",
          gray: "#86868a",
          darkgray: "#d8d8d6",
          dark: "#f0f0ee",
          secondary: "#5fe0ac",
          tertiary: "#5fe0ac",
          highlight: "rgba(95, 224, 172, 0.12)",
          textHighlight: "#5fe0ac44",
        },
      },
    },
  },
  plugins: {
    transformers: [
      Plugin.FrontMatter(),
      Plugin.CreatedModifiedDate({
        priority: ["frontmatter", "git", "filesystem"],
      }),
      Plugin.SyntaxHighlighting({
        theme: {
          light: "github-light",
          dark: "github-dark",
        },
        keepBackground: false,
      }),
      Plugin.ObsidianFlavoredMarkdown({ enableInHtmlEmbed: false }),
      Plugin.GitHubFlavoredMarkdown(),
      Plugin.TableOfContents(),
      Plugin.CrawlLinks({ markdownLinkResolution: "shortest" }),
      Plugin.Description(),
      Plugin.Latex({ renderEngine: "katex" }),
    ],
    filters: [Plugin.RemoveDrafts()],
    emitters: [
      Plugin.AliasRedirects(),
      Plugin.ComponentResources(),
      Plugin.ContentPage(),
      Plugin.FolderPage(),
      Plugin.TagPage(),
      Plugin.ContentIndex({
        enableSiteMap: true,
        enableRSS: true,
      }),
      Plugin.Assets(),
      Plugin.Static(),
      Plugin.Favicon(),
      Plugin.NotFoundPage(),
      // Comment out CustomOgImages to speed up build time
      Plugin.CustomOgImages(),
      Plugin.LlmsTxt(),
    ],
  },
}

export default config
