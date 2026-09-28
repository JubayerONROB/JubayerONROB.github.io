function renderPixelHero(canvas: HTMLCanvasElement, image: HTMLImageElement) {
  // Subject bounding box in the SOURCE photo's own pixel coordinates
  // (the vendored landing-photo.jpg is 1400x1867). Used to center the
  // crop on the subject and to keep glitch patches off the face.
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

    // crop source image to match the canvas's aspect ratio, centered on
    // the subject rather than the geometric center of the photo
    const screenRatio = W / H
    let sw: number, sh: number
    if (image.naturalWidth / image.naturalHeight > screenRatio) {
      sh = image.naturalHeight
      sw = sh * screenRatio
    } else {
      sw = image.naturalWidth
      sh = sw / screenRatio
    }

    const subjectCenterX = (SUBJECT_BOX.x0 + SUBJECT_BOX.x1) / 2
    const subjectCenterY = (SUBJECT_BOX.y0 + SUBJECT_BOX.y1) / 2
    const sx = Math.max(0, Math.min(image.naturalWidth - sw, subjectCenterX - sw / 2))
    const sy = Math.max(0, Math.min(image.naturalHeight - sh, subjectCenterY - sh / 2))

    ctx.drawImage(image, sx, sy, sw, sh, 0, 0, W, H)

    // map the subject box from source-photo pixel coordinates into the
    // current crop/canvas space so glitch patches stay off the face
    const normX0 = Math.max(0, Math.min(1, (SUBJECT_BOX.x0 - sx) / sw))
    const normX1 = Math.max(0, Math.min(1, (SUBJECT_BOX.x1 - sx) / sw))
    const normY0 = Math.max(0, Math.min(1, (SUBJECT_BOX.y0 - sy) / sh))
    const normY1 = Math.max(0, Math.min(1, (SUBJECT_BOX.y1 - sy) / sh))

    const boxX0 = normX0 * W
    const boxX1 = normX1 * W
    const boxY0 = normY0 * H
    const boxY1 = normY1 * H

    // a handful of small pixelated glitch patches scattered around the
    // frame — a static, one-off accent, kept out of the subject's region
    // so they never land on the face
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

      // sample the source at very low resolution for a blocky look
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
