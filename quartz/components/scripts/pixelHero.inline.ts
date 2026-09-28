function renderPixelHero(canvas: HTMLCanvasElement, image: HTMLImageElement) {
  // Subject bounding box in the SOURCE photo's own pixel coordinates
  // (the vendored landing-photo.jpg is 1400x1867). Everything inside this
  // box stays sharp; everything outside is blurred.
  const SUBJECT_BOX = { x0: 345, y0: 885, x1: 925, y1: 1867 }

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

    // blurred background layer
    const blurPx = Math.max(4, Math.min(W, H) * 0.02)
    ctx.filter = `blur(${blurPx}px)`
    ctx.drawImage(image, sx, sy, sw, sh, 0, 0, W, H)
    ctx.filter = "none"

    // map the subject box from source-photo pixel coordinates into the
    // current crop/canvas space so it stays correct across resizes
    const normX0 = Math.max(0, Math.min(1, (SUBJECT_BOX.x0 - sx) / sw))
    const normX1 = Math.max(0, Math.min(1, (SUBJECT_BOX.x1 - sx) / sw))
    const normY0 = Math.max(0, Math.min(1, (SUBJECT_BOX.y0 - sy) / sh))
    const normY1 = Math.max(0, Math.min(1, (SUBJECT_BOX.y1 - sy) / sh))

    const boxX0 = normX0 * W
    const boxX1 = normX1 * W
    const boxY0 = normY0 * H
    const boxY1 = normY1 * H

    // overlay the subject at full sharpness, feathered into the blurred backdrop
    if (boxX1 > boxX0 && boxY1 > boxY0) {
      const sharpCanvas = document.createElement("canvas")
      sharpCanvas.width = W
      sharpCanvas.height = H
      const sharpCtx = sharpCanvas.getContext("2d")

      const maskCanvas = document.createElement("canvas")
      maskCanvas.width = W
      maskCanvas.height = H
      const maskCtx = maskCanvas.getContext("2d")

      if (sharpCtx && maskCtx) {
        sharpCtx.drawImage(image, sx, sy, sw, sh, 0, 0, W, H)

        // a soft-cornered shape open at the bottom (the subject extends
        // past the frame), blurred to feather into the blurred backdrop
        const feather = Math.max(8, Math.min(W, H) * 0.025)
        const radius = Math.min(boxX1 - boxX0, boxY1 - boxY0) * 0.35
        maskCtx.filter = `blur(${feather}px)`
        maskCtx.fillStyle = "#fff"
        maskCtx.beginPath()
        maskCtx.moveTo(boxX0, boxY0 + radius)
        maskCtx.arcTo(boxX0, boxY0, boxX0 + radius, boxY0, radius)
        maskCtx.lineTo(boxX1 - radius, boxY0)
        maskCtx.arcTo(boxX1, boxY0, boxX1, boxY0 + radius, radius)
        maskCtx.lineTo(boxX1, H)
        maskCtx.lineTo(boxX0, H)
        maskCtx.closePath()
        maskCtx.fill()

        sharpCtx.globalCompositeOperation = "destination-in"
        sharpCtx.drawImage(maskCanvas, 0, 0)

        ctx.drawImage(sharpCanvas, 0, 0)
      }
    }

    // a handful of small pixelated glitch patches scattered around the
    // frame — a static, one-off accent, not a full pixelated background.
    // Kept out of the subject's sharp region so they never land on the face.
    const glitchCount = 5
    for (let i = 0; i < glitchCount; i++) {
      const patchSize = (Math.min(W, H) * (0.05 + Math.random() * 0.06)) | 0

      let px = 0
      let py = 0
      let placed = false
      for (let attempt = 0; attempt < 8; attempt++) {
        px = Math.random() * (W - patchSize)
        py = Math.random() * (H - patchSize)
        const overlapsSubject =
          px < boxX1 && px + patchSize > boxX0 && py < boxY1 && py + patchSize > boxY0
        if (!overlapsSubject) {
          placed = true
          break
        }
      }
      if (!placed) continue

      // sample the sharp source at very low resolution for a blocky look
      const blockGrid = 5
      const blockCanvas = document.createElement("canvas")
      blockCanvas.width = blockGrid
      blockCanvas.height = blockGrid
      const blockCtx = blockCanvas.getContext("2d")
      if (!blockCtx) continue

      // map this patch back into source-image coordinates
      const srcPatchX = sx + (px / W) * sw
      const srcPatchY = sy + (py / H) * sh
      const srcPatchSize = (patchSize / W) * sw

      blockCtx.drawImage(
        image,
        srcPatchX,
        srcPatchY,
        srcPatchSize,
        srcPatchSize,
        0,
        0,
        blockGrid,
        blockGrid,
      )

      ctx.imageSmoothingEnabled = false
      ctx.drawImage(blockCanvas, 0, 0, blockGrid, blockGrid, px, py, patchSize, patchSize)
      ctx.imageSmoothingEnabled = true
    }
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
