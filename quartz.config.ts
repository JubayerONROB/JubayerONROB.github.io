import { QuartzConfig } from "./quartz/cfg"
import * as Plugin from "./quartz/plugins"

/**
 * Quartz 4 Configuration
 *
 * See https://quartz.jzhao.xyz/configuration for more information.
 */
const config: QuartzConfig = {
  configuration: {
    pageTitle: "A. J. A. Jubayer Talukder",
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
        // Departure Mono is self-hosted (see quartz/styles/custom.scss and
        // quartz/static/fonts/) since it isn't distributed via Google Fonts.
        header: "Departure Mono",
        body: "Roboto Mono",
        code: "Ubuntu Mono",
      },
      colors: {
        // Clean white / near-black canvas with a single violet accent.
        lightMode: {
          light: "#ffffff",
          lightgray: "#e6e6e9",
          gray: "#8a8a90",
          darkgray: "#3a3a3e",
          dark: "#1a1a1c",
          secondary: "#7820bf",
          tertiary: "#7820bf",
          highlight: "rgba(120, 32, 191, 0.08)",
          textHighlight: "#e9ff0088",
        },
        darkMode: {
          light: "#0e0e10",
          lightgray: "#26262a",
          gray: "#8a8a90",
          darkgray: "#e8e8ea",
          dark: "#ffffff",
          secondary: "#a855f7",
          tertiary: "#a855f7",
          highlight: "rgba(168, 85, 247, 0.14)",
          textHighlight: "#e9ff0044",
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
