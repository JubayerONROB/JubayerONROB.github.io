function renderPixelHero(canvas: HTMLCanvasElement, image: HTMLImageElement) {
  // Resolution of the luminance buffer the line-render is sampled from.
  const GRID_WIDTH = 170

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

    const pixels = smallCtx.getImageData(0, 0, GRID_WIDTH, gridHeight)
    const data = pixels.data

    function brightnessAt(col: number, row: number): number {
      const i = (row * GRID_WIDTH + col) * 4
      const r = data[i]
      const g = data[i + 1]
      const b = data[i + 2]
      let brightness = 0.2126 * r + 0.7152 * g + 0.0722 * b
      brightness = (brightness - 128) * 1.25 + 128 + 25
      return Math.max(0, Math.min(255, brightness)) / 255
    }

    function tintColor(brightness: number): string {
      const v = brightness * 255
      const tint = 0.07
      const r = Math.min(255, v * (1 - tint))
      const g = Math.min(255, v * (1 - tint * 0.1))
      const b = Math.min(255, v * (1 + tint))
      return `rgb(${r | 0}, ${g | 0}, ${b | 0})`
    }

    // base fill — the darkest tone in the piece, so low-brightness cells
    // (hair, shadow, jacket creases) read as near-solid bars
    ctx.fillStyle = "#1c2226"
    ctx.fillRect(0, 0, W, H)

    const rowHeight = H / gridHeight
    const colWidth = W / GRID_WIDTH

    for (let row = 0; row < gridHeight; row++) {
      const rowY = row * rowHeight
      const rowCenter = rowY + rowHeight / 2
      // brick-style stagger so dashes don't line up into a grid
      const stagger = row % 2 === 0 ? 0 : colWidth * 0.5

      for (let col = 0; col < GRID_WIDTH; col++) {
        const brightness = brightnessAt(col, row)

        // darker source pixels -> thicker line (more "ink"); bright
        // pixels -> thin, sparse line so the background reads as open space
        const thickness = rowHeight * (0.12 + (1 - brightness) * 0.8)
        // ragged dash length instead of a uniform block
        const dashWidth = colWidth * (0.65 + Math.random() * 0.35)

        ctx.fillStyle = tintColor(brightness)
        ctx.fillRect(
          col * colWidth + stagger,
          rowCenter - thickness / 2,
          dashWidth,
          Math.max(1, thickness),
        )
      }
    }

    // faint decorative data readout in the open background area (right side
    // of the frame, where the source photo is plain wall rather than subject)
    ctx.font = "9px monospace"
    const hexChars = "0123456789abcdef"
    for (let gy = 0; gy < H; gy += 14) {
      for (let gx = W * 0.55; gx < W; gx += 12) {
        const col = Math.min(GRID_WIDTH - 1, Math.floor((gx / W) * GRID_WIDTH))
        const row = Math.min(gridHeight - 1, Math.floor((gy / H) * gridHeight))
        const brightness = brightnessAt(col, row)
        if (brightness > 0.55 && Math.random() < 0.3) {
          ctx.fillStyle = `rgba(150, 190, 200, ${0.08 + Math.random() * 0.1})`
          ctx.fillText(hexChars[(Math.random() * hexChars.length) | 0], gx, gy)
        }
      }
    }

    // static row-glitch: a handful of one-off horizontal displacements,
    // computed once per render (not animated)
    const glitchPasses = 6
    for (let i = 0; i < glitchPasses; i++) {
      const y = Math.random() * H
      const stripHeight = Math.random() * 3 + 1
      const offset = (Math.random() - 0.5) * 18
      ctx.drawImage(canvas, 0, y, W, stripHeight, offset, y, W, stripHeight)
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
