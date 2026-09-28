function renderPixelHero(canvas: HTMLCanvasElement, image: HTMLImageElement) {
  // Resolution of the color buffer the pixel-art render is sampled from.
  // Lower = chunkier pixels.
  const GRID_WIDTH = 110

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

    const gridHeight = Math.round((GRID_WIDTH * image.naturalHeight) / image.naturalWidth)

    const smallCanvas = document.createElement("canvas")
    smallCanvas.width = GRID_WIDTH
    smallCanvas.height = gridHeight
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

    smallCtx.drawImage(image, sx, sy, sw, sh, 0, 0, GRID_WIDTH, gridHeight)

    // boost saturation and contrast a touch so the chunky pixels read as
    // vivid color blocks rather than a slightly washed-out photo
    const pixels = smallCtx.getImageData(0, 0, GRID_WIDTH, gridHeight)
    const data = pixels.data
    for (let i = 0; i < data.length; i += 4) {
      const r = data[i]
      const g = data[i + 1]
      const b = data[i + 2]
      const gray = 0.2126 * r + 0.7152 * g + 0.0722 * b
      const saturation = 1.35
      const contrast = 1.12
      for (let c = 0; c < 3; c++) {
        const channel = data[i + c]
        let v = gray + (channel - gray) * saturation
        v = (v - 128) * contrast + 128
        data[i + c] = Math.max(0, Math.min(255, v))
      }
    }
    smallCtx.putImageData(pixels, 0, 0)

    // draw the low-res color buffer scaled up with smoothing disabled —
    // this is what produces the blocky retro pixel-art look
    ctx.imageSmoothingEnabled = false
    ctx.drawImage(smallCanvas, 0, 0, W, H)

    // gentle vignette to frame the image against the page background
    const gradient = ctx.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 0.9)
    gradient.addColorStop(0, "rgba(0, 0, 0, 0)")
    gradient.addColorStop(1, "rgba(0, 0, 0, 0.25)")
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
