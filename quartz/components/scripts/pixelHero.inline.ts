function renderPixelHero(canvas: HTMLCanvasElement, image: HTMLImageElement) {
  const PIXEL_WIDTH = 220

  function draw() {
    const rect = canvas.getBoundingClientRect()
    const dpr = Math.min(window.devicePixelRatio || 1, 2)
    const W = Math.round(rect.width * dpr)
    const H = Math.round(rect.height * dpr)
    if (W === 0 || H === 0) return

    canvas.width = W
    canvas.height = H

    const ctx = canvas.getContext("2d", { alpha: false })
    if (!ctx) return

    const smallWidth = PIXEL_WIDTH
    const smallHeight = Math.round((PIXEL_WIDTH * image.naturalHeight) / image.naturalWidth)

    const smallCanvas = document.createElement("canvas")
    smallCanvas.width = smallWidth
    smallCanvas.height = smallHeight
    const smallCtx = smallCanvas.getContext("2d")
    if (!smallCtx) return

    // crop source image to match the canvas's aspect ratio
    const imageRatio = image.naturalWidth / image.naturalHeight
    const screenRatio = W / H
    let sx: number, sy: number, sw: number, sh: number
    if (imageRatio > screenRatio) {
      sh = image.naturalHeight
      sw = sh * screenRatio
      sx = (image.naturalWidth - sw) / 2
      sy = 0
    } else {
      sw = image.naturalWidth
      sh = sw / screenRatio
      sx = 0
      sy = (image.naturalHeight - sh) / 2
    }

    smallCtx.drawImage(image, sx, sy, sw, sh, 0, 0, smallWidth, smallHeight)

    const pixels = smallCtx.getImageData(0, 0, smallWidth, smallHeight)
    const data = pixels.data

    for (let i = 0; i < data.length; i += 4) {
      const r = data[i]
      const g = data[i + 1]
      const b = data[i + 2]

      let brightness = 0.2126 * r + 0.7152 * g + 0.0722 * b
      brightness = (brightness - 128) * 1.45 + 128
      brightness = Math.max(0, Math.min(255, brightness))

      const tint = 0.1
      data[i] = Math.min(255, brightness * (1 - tint))
      data[i + 1] = Math.min(255, brightness * (1 - tint * 0.1))
      data[i + 2] = Math.min(255, brightness * (1 + tint))
    }

    smallCtx.putImageData(pixels, 0, 0)

    ctx.fillStyle = "#111"
    ctx.fillRect(0, 0, W, H)
    ctx.imageSmoothingEnabled = false
    ctx.drawImage(smallCanvas, 0, 0, W, H)

    // static scanlines (drawn once, not animated)
    ctx.fillStyle = "rgba(255, 255, 255, 0.035)"
    for (let y = 0; y < H; y += 5) {
      ctx.fillRect(0, y, W, 1)
    }

    // vignette
    const gradient = ctx.createRadialGradient(W / 2, H / 2, H * 0.25, W / 2, H / 2, H * 0.8)
    gradient.addColorStop(0, "rgba(0, 0, 0, 0)")
    gradient.addColorStop(1, "rgba(0, 0, 0, 0.45)")
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, W, H)
  }

  if (image.complete) {
    draw()
  } else {
    image.onload = draw
  }

  let resizeTimeout: ReturnType<typeof setTimeout>
  const onResize = () => {
    clearTimeout(resizeTimeout)
    resizeTimeout = setTimeout(draw, 100)
  }
  window.addEventListener("resize", onResize)
  window.addCleanup(() => {
    clearTimeout(resizeTimeout)
    window.removeEventListener("resize", onResize)
  })
}

document.addEventListener("nav", () => {
  const canvas = document.querySelector<HTMLCanvasElement>("[data-pixel-hero-src]")
  const src = canvas?.dataset.pixelHeroSrc
  if (!canvas || !src) return

  const image = new Image()
  image.src = src
  renderPixelHero(canvas, image)
})
