import { pathToRoot, joinSegments } from "../util/path"
import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
// @ts-ignore
import script from "./scripts/pixelHero.inline"
import style from "./styles/pixelHero.scss"

const PixelHero: QuartzComponent = ({ fileData, displayClass }: QuartzComponentProps) => {
  if (fileData.slug !== "index") {
    return null
  }

  const src = joinSegments(pathToRoot(fileData.slug), "static/images/landing-photo.jpg")

  return (
    <div class={`pixel-hero ${displayClass ?? ""}`}>
      <canvas data-pixel-hero-src={src}></canvas>
    </div>
  )
}

PixelHero.css = style
PixelHero.afterDOMLoaded = script

export default (() => PixelHero) satisfies QuartzComponentConstructor
