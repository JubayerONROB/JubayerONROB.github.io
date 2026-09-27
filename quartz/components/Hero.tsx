import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import style from "./styles/hero.scss"

const Hero: QuartzComponent = ({ fileData, displayClass }: QuartzComponentProps) => {
  if (fileData.slug !== "index") {
    return null
  }

  return (
    <div class={`hero-diagram ${displayClass ?? ""}`}>
      <svg viewBox="0 0 640 320" role="img" aria-label="Jubayer's technical disciplines: AI, Robotics and Hardware, converging into Systems">
        {/* connecting lines */}
        <path class="hero-line" d="M 320 70 L 140 150" />
        <path class="hero-line" d="M 320 70 L 320 150" />
        <path class="hero-line" d="M 320 70 L 500 150" />
        <path class="hero-line hero-line-out" d="M 140 180 L 320 240" />
        <path class="hero-line hero-line-out" d="M 320 180 L 320 240" />
        <path class="hero-line hero-line-out" d="M 500 180 L 320 240" />

        {/* root node */}
        <g class="hero-node hero-node-root">
          <circle cx="320" cy="60" r="38" />
          <text x="320" y="64" text-anchor="middle">
            JUBAYER
          </text>
        </g>

        {/* branch nodes */}
        <a href="/tags/ai" class="hero-node hero-node-branch" aria-label="AI projects and research">
          <rect x="80" y="150" width="120" height="34" rx="4" />
          <text x="140" y="172" text-anchor="middle">
            AI
          </text>
        </a>
        <a href="/tags/robotics" class="hero-node hero-node-branch" aria-label="Robotics and UAV projects">
          <rect x="260" y="150" width="120" height="34" rx="4" />
          <text x="320" y="172" text-anchor="middle">
            ROBOTICS
          </text>
        </a>
        <a href="/tags/vlsi" class="hero-node hero-node-branch" aria-label="Hardware and VLSI projects">
          <rect x="440" y="150" width="120" height="34" rx="4" />
          <text x="500" y="172" text-anchor="middle">
            HARDWARE
          </text>
        </a>

        {/* systems node */}
        <a href="/projects" class="hero-node hero-node-systems" aria-label="See all systems and projects">
          <rect x="245" y="240" width="150" height="36" rx="4" />
          <text x="320" y="263" text-anchor="middle">
            SYSTEMS
          </text>
        </a>
      </svg>
    </div>
  )
}

Hero.css = style

export default (() => Hero) satisfies QuartzComponentConstructor
