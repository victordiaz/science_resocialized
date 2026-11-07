/** /lab: the brand kit in one place. Not linked from the menus. */
import { Loader, LoaderKind } from "../ui";

const B = "/brand";

const COLORS: [string, string, string][] = [
  ["Ink", "--sr-ink", "#1B1C1F"],
  ["Ground", "--sr-ground", "#F3F2EE"],
  ["Surface", "--sr-surface", "#FFFFFF"],
  ["Line", "--sr-line", "#E2E0D9"],
  ["Muted", "--sr-muted", "#5E6066"],
  ["Link", "--sr-link", "#A9A79F"],
  ["Blue", "--sr-blue", "#1F5FD6"],
  ["Teal", "--sr-teal", "#0B7285"],
  ["Clay", "--sr-clay", "#B4410B"],
  ["Purple", "--sr-purple", "#6741D9"],
  ["Success", "--sr-success", "#2B8A3E"],
  ["Blue on dark", "--sr-blue-on-dark", "#4C8DFF"],
  ["Teal on dark", "--sr-teal-on-dark", "#22B8CF"],
  ["Clay on dark", "--sr-clay-on-dark", "#FF8A4C"],
  ["Purple on dark", "--sr-purple-on-dark", "#9775FA"],
];

const ANIMATIONS: [LoaderKind, string][] = [
  ["gather", "Splash, first launch, empty pages"],
  ["thinking", "General loading"],
  ["signals", "A review is running"],
  ["orbit", "Long waits, such as a replication"],
  ["reply", "A persona just replied"],
  ["verified", "Replication verified, task done"],
  ["waiting", "Paused, needs you (leak check)"],
];

type Asset = { file: string; label: string; dark?: boolean; w?: number };

const MARKS: Asset[] = [
  { file: "logo/mark.svg", label: "Mark" },
  { file: "logo/mark-on-dark.svg", label: "Mark on dark", dark: true },
  { file: "logo/mark-black.svg", label: "Black" },
  { file: "logo/mark-white.svg", label: "White", dark: true },
];

const LOCKUPS: Asset[] = [
  { file: "lockup/lockup-horizontal.svg", label: "Horizontal", w: 280 },
  { file: "lockup/lockup-horizontal-on-dark.svg", label: "Horizontal on dark", dark: true, w: 280 },
  { file: "lockup/lockup-horizontal-black.svg", label: "Horizontal, black", w: 280 },
  { file: "lockup/lockup-horizontal-white.svg", label: "Horizontal, white", dark: true, w: 280 },
  { file: "lockup/lockup-stacked.svg", label: "Stacked", w: 160 },
  { file: "lockup/lockup-stacked-on-dark.svg", label: "Stacked on dark", dark: true, w: 160 },
];

const ICONS: Asset[] = [
  { file: "app-icon/app-icon.svg", label: "App icon" },
  { file: "app-icon/app-icon-dark.svg", label: "Dark" },
  { file: "app-icon/app-icon-cream.svg", label: "Cream" },
  { file: "app-icon/maskable.svg", label: "Maskable (PWA)" },
];

function Tile({ a, size = 96 }: { a: Asset; size?: number }) {
  return (
    <figure className={`lab-tile${a.dark ? " dark" : ""}`}>
      <div className="lab-art">
        <img src={`${B}/${a.file}`} alt={a.label} style={{ width: a.w ?? size, height: "auto" }} />
      </div>
      <figcaption>
        <span>{a.label}</span>
        <a href={`${B}/${a.file}`} download className="muted small">{a.file.split("/").pop()}</a>
      </figcaption>
    </figure>
  );
}

export default function Lab() {
  return (
    <div className="lab-scroll"><div className="lab">
      <header className="lab-head">
        <img src={`${B}/lockup/lockup-horizontal.svg`} alt="Science Resocialized" width={300} />
        <p className="muted">
          The brand kit. The mark is a paper in the middle linked to four reviewers. Files live in{" "}
          <code>frontend/public/brand/</code>; <a href={`${B}/README.md`}>usage rules</a>.
        </p>
      </header>

      <section>
        <h2>Animations</h2>
        <p className="muted small">Shown at 24 px, the size they're used at, and at 96 px. Each one stops when reduced motion is on.</p>
        <div className="lab-anims">
          {ANIMATIONS.map(([k, use]) => (
            <figure key={k} className="lab-tile">
              <div className="lab-art">
                <Loader kind={k} size={96} label={k} />
                <Loader kind={k} size={24} />
              </div>
              <figcaption>
                <span>{k}</span>
                <span className="muted small">{use}</span>
              </figcaption>
            </figure>
          ))}
        </div>
      </section>

      <section>
        <h2>Mark</h2>
        <p className="muted small">Smallest size 16 px. Below 32 px use the favicon version.</p>
        <div className="lab-grid">{MARKS.map((a) => <Tile key={a.file} a={a} />)}</div>
      </section>

      <section>
        <h2>Lockups</h2>
        <p className="muted small">Smallest width for the horizontal logo: 120 px.</p>
        <div className="lab-grid wide">{LOCKUPS.map((a) => <Tile key={a.file} a={a} />)}</div>
      </section>

      <section>
        <h2>App icons and favicon</h2>
        <div className="lab-grid">
          {ICONS.map((a) => <Tile key={a.file} a={a} />)}
          <figure className="lab-tile">
            <div className="lab-art lab-fav">
              {[16, 32, 48].map((s) => (
                <img key={s} src={`${B}/favicon/favicon-${s}.png`} width={s} height={s} alt={`${s} px`} />
              ))}
            </div>
            <figcaption>
              <span>Favicon 16, 32, 48</span>
              <a href={`${B}/favicon/favicon.ico`} download className="muted small">favicon.ico</a>
            </figcaption>
          </figure>
        </div>
      </section>

      <section>
        <h2>Social</h2>
        <div className="lab-grid wide">
          <Tile a={{ file: "social/og-image.png", label: "Link preview, 1200 × 630", w: 360 }} />
          <Tile a={{ file: "social/avatar.png", label: "Avatar", w: 140 }} />
          <Tile a={{ file: "social/avatar-light.png", label: "Avatar, light", w: 140 }} />
        </div>
      </section>

      <section>
        <h2>Colors</h2>
        <p className="muted small">
          As CSS variables in <a href={`${B}/colors.css`}>colors.css</a>.
        </p>
        <div className="lab-colors">
          {COLORS.map(([name, v, hex]) => (
            <div key={v} className="lab-swatch">
              <span style={{ background: hex }} />
              <strong>{name}</strong>
              <code>{hex}</code>
              <code className="muted">{v}</code>
            </div>
          ))}
        </div>
      </section>
    </div></div>
  );
}
