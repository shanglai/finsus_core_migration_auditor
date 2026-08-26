# Linko Design System

Linko is a Mexican enterprise technology firm (Mexico City, founded 2002) that sells
integration, cybersecurity, cloud & data, digital transformation and AI services to
large regulated companies — banks, insurers, retailers, logistics operators. Its
positioning line is **"Soluciones tecnológicas simplificadas"** / *"Tech solutions made
simple"*, and its public face is a single bilingual marketing site.

## Sources used

| Source | What it gave |
| --- | --- |
| `uploads/Captura de pantalla 2026-08-09 a la(s) 9.02.54 p.m..png` | Home hero, floating nav, button pair, ring motif |
| `uploads/…9.03.32 p.m..png` | About-page history timeline card, year chips, lime illustration accent |
| `uploads/…9.03.40 p.m..png` | Photo panel, footer, mark, translucent nav over imagery |
| <https://linko.ai/en/> and <https://linko.ai/> | Verbatim site copy: nav, stats, service lines, success cases, industries, partner list and blurbs, footer |

**No codebase, Figma file or brand manual was provided.** Colour values are pixel-sampled
from the screenshots; spacing, radii and type sizes are visual estimates from full-page
captures rendered at 2842px wide. Treat every number in `tokens/` as a good first
approximation, not a spec — see *Open questions* at the bottom.

## Index

- `styles.css` — the single entry point consumers link. Imports everything below.
- `tokens/` — `fonts.css`, `colors.css`, `typography.css`, `spacing.css`, `radius.css`, `elevation.css`, `motion.css`
- `guidelines/` — foundation specimen cards (colour, type, spacing, radii, elevation, logo, motion, imagery)
- `components/` — React primitives, grouped `core` / `layout` / `content` / `brand`
- `ui_kits/website/` — click-through recreation of linko.ai
- `assets/` — `linko-logo.png` (lockup), `linko-mark.png` (mark), `photo-team.jpg`
- `thumbnail.html` — homepage tile
- `SKILL.md` — Agent Skills wrapper

### Components

**core** — `Button`, `ArrowButton`, `ArrowLink`, `Chip`, `LangToggle`
**layout** — `NavBar`, `Footer`, `SectionHeading`
**content** — `StatBlock`, `SolutionCard`, `CaseCard`, `IndustryCard`, `PartnerTile`, `TimelineCard`
**brand** — `RingMotif`

Every component has a sibling `.d.ts` (props contract) and `.prompt.md` (one-line
what & when, usage snippet, variants).

#### Intentional additions

The sources define no formal component library, so the inventory above was derived by
enumerating every distinct repeated element visible in the three screenshots and on the
live site. Two entries go slightly beyond what a screenshot literally shows:

- **`RingMotif`** — the hero's field of overlapping outlined circles, parameterised. It is
  reproduced, not invented, but the real site may render it as a static SVG.
- **`Chip`** — the timeline year pill generalised to a static label component.

No Toast, Avatar, Tabs, Modal or Tooltip has been authored: nothing in the sources shows one.

---

## Content fundamentals

**Language.** Spanish first, English second, with a hard Esp/Eng switch in the nav rather
than a blended page. The English is a straight translation of the Spanish, not separate
copy. Register is the same in both: *usted*-free, informal-professional **tú** ("te
ofrecemos", "tu tecnología", "cuéntanos"). Never *usted*.

**Person.** "We" for Linko ("Entendemos que…", "En Linko aprovechamos…"), "you" for the
reader ("…te ayudará a crear mejores experiencias"). Never "I". The customer is always the
subject of the benefit; Linko is the subject of the capability.

**Casing.** Sentence case everywhere — headlines, card titles, buttons, nav. The only
capitalised-word exceptions are proper nouns and product names ("Cloud & Data", "UiPath").
No ALL CAPS, no Title Case Headlines. Eyebrows are sentence case too ("Nuestra oferta").

**Punctuation.** Headlines take no terminal period ("Casos de éxito", "Transformamos
industrias"). Body paragraphs and bullets do. The footer tagline is the one headline that
carries a period, because it is a sentence: "Take the next step, simplified solutions."

**Sentence shape.** Short declaratives. One idea per sentence, no subordinate stacking, no
rhetorical questions, no "not just X — Y" constructions. The longest sentence on the site
is 34 words.

**Numbers carry the argument.** Proof is always a bare figure plus a noun phrase: "20+ /
Años de experiencia", "100+ / Millones de clientes finales impactados". Case-study bullets
always lead with the number: "20% menos trabajo manual…", "6 semanas para desplegar…",
"2x más rápido…". Never a percentage buried mid-sentence.

**Verbs.** Imperative in industry blurbs ("Entrega ofertas…", "Elimina tareas…",
"Optimiza recursos…"), declarative everywhere else.

**CTAs.** Exactly two labels do all the work: **Contáctanos** (primary, everywhere) and
**Soluciones / Conoce más** (secondary). CTAs are one or two words, no "Learn more about
our…", no exclamation marks.

**Emoji: none.** Not on the site, not in headings, not in cards. Do not introduce them.
(Linko's LinkedIn posts do use emoji and hashtags — that is a social-channel voice, not
the brand's product voice.)

**Vibe.** Calm, plain, slightly understated. The brand promise is *simplification*, so the
writing performs it: nothing florid, no metaphors about journeys or unlocking potential,
no exclamation. Where a competitor would write "Revolutionise your enterprise with
next-generation AI", Linko writes "Automatiza el trabajo repetitivo".

---

## Visual foundations

**Palette.** One saturated brand green — `#02b101` — against a deep teal-navy ink
`#09353b`, on an off-white page `#f8faf8` with `#f2f2f2` chrome. A single lime
`#addb4f` appears **only inside illustrations**, never as a fill or a text colour. There
is no third brand hue, no purple, no gradient. Green is used at full strength: as a solid
button fill, as link and eyebrow text, as an entire panel (the timeline card's right half),
and as the logo colour. Ink is used for headings, dark pills, and the selected state of the
language toggle.

**Type.** A single neo-grotesque family at four weights. Display and section headlines are
set at **regular (400)** — never bold — at 44–76px with `-0.02em` tracking, which is what
gives the site its quiet, editorial feel. Medium (500) appears only on small UI labels.
Line-height is tight on display (1.04–1.12) and generous in body (1.5–1.55). Measure is
capped: headlines ~12–22ch, body ~60ch. See the substitution note below.

**Layout.** A centred 1440px container with a 36px page margin. The nav is **fixed**,
floating, and inset from all three top edges — it never spans full-bleed. Sections stack
on a ~112px vertical rhythm. Hero and positioning sections are two-column 50/50; service
and case grids are three-up; industries and partners are four-up. Content is left-aligned
by default; centring is reserved for the ring motif.

**Corners.** Everything is round. Controls, chips, nav bar and the language toggle are full
pills (`999px`). Cards and media panels are 28px; large photo blocks 40px; small inputs
and inner tiles 12–20px. There is no sharp corner anywhere in the system.

**Cards.** White on the off-white page, 28px radius, 32px padding, **no border**, and a
very wide low-opacity shadow (`0 2px 24px rgba(9,53,59,.05)`). Hover raises the card 4px
and deepens the shadow to `0 8px 40px rgba(9,53,59,.08)`. The system is essentially flat:
there are no inner shadows, no bevels, no glows, and no coloured left borders.

**Backgrounds.** Flat colour only — off-white page, `#f2f2f2` chrome for nav and footer,
solid green for emphasis panels. No gradients, no repeating patterns, no textures, no
noise. The only "decoration" is the ring motif: a 3×2 field of thin outlined circles that
overlap slightly, one of them lime, sitting in the right half of the hero. It is an
abstraction of the two interlocking rings in the mark.

**Imagery.** Warm, naturally-lit, candid workplace photography — hands, tablets, wooden
desks, mid-conversation moments, shot slightly wide. Colour is warm and true, not graded,
not black-and-white, no grain, no duotone. Photos always sit inside a rounded panel
(28–40px), never full-bleed to the viewport edge, and are frequently overlapped by a small
white caption card with a short sentence in it.

**Transparency and blur.** Used in exactly one place: when the fixed nav passes over a
photograph it becomes a frosted panel (`rgba(242,242,242,.72)` + `blur(18px)`). Over flat
backgrounds it is fully opaque. There are no scrims or protection gradients on imagery —
readability is solved with the white caption card instead.

**Motion.** Restrained and short. 120ms for state flips, 220ms for hovers and colour
changes, 420ms for panel/carousel transitions, on `cubic-bezier(.4,0,.2,1)` for controls
and `cubic-bezier(.16,1,.3,1)` for anything that travels. Fades and small translations
only — no bounce, no spring, no parallax, no scroll-jacking.

**Hover states.** Filled buttons darken (`#02b101` → `#019701`); outlined buttons fill with
the lightest green tint; ghost items take the neutral chrome tint; text links lose ~25%
opacity and their trailing arrow slides 4px further out; cards lift.

**Press states.** Uniform `scale(0.97)` with the hover colour retained. No colour change on
press, no ripple.

**Borders.** Hairline `1px` only, in `#e6e7e6`, and only where a container must be
separated without a shadow: the language toggle, partner tiles, form inputs, the footer
legal rule. Brand-green 1px borders define the secondary button and the selected partner tile.

**Focus.** Green ring on the brand colour; never remove the outline.

---

## Iconography

**There is no icon library in the provided sources, and no icon font.** What the screenshots
and the site actually contain is:

1. **A right-pointing arrow**, used constantly — trailing every CTA button, inside the
   circular nav button, and after every "Conoce más" link. It is a thin (2px), round-capped,
   flat-terminal arrow. This is the only true UI glyph in the system. It is drawn inline in
   `components/core/ArrowButton.jsx` / `Button.jsx` at Lucide's `arrow-right` proportions
   (24px box, 2px stroke, round caps) — **flagged as a substitution**; if Linko has its own
   arrow asset, drop it in and replace the inline path.
2. **Full-colour PNG illustrations** for the five service lines (Ciberseguridad,
   Integración, Cloud & Data, Transformación digital, AI) and the four industries. These are
   hosted on `linko.ai/wp-content/uploads/2024/…` and **could not be downloaded into this
   project**. `SolutionCard` and `IndustryCard` accept an `iconSrc` and fall back to an
   outlined-circle placeholder that matches the ring motif — deliberately neutral, so a
   placeholder never reads as a real Linko icon.
3. **Third-party partner logos** (Thales, UiPath, Actico, Salesforce, MuleSoft, TIBCO,
   Google Cloud, Grafana) and social icons (Facebook, WhatsApp, LinkedIn, Instagram), also
   hosted PNGs. `PartnerTile` degrades to the partner name set in type. **Never redraw a
   third-party mark.**

**Emoji and unicode as icons: never.** The one non-alphabetic character used as an ornament
is the pipe `|` separating the footer legal links.

**If you need a UI icon that does not exist here**, use Lucide from CDN at 2px stroke,
round caps, 24px box — it is the closest match to the arrow's construction — and say so in
your handoff.

---

## Assets

- `assets/linko-logo.png` — horizontal lockup (green mark + ink wordmark), extracted from the
  site header. Clear space ≥ the mark's height. On dark surfaces, knock the lockup out to white.
- `assets/linko-mark.png` — the mark alone: two interlocking rings inside a lens/eye outline.
- `assets/photo-team.jpg` — one representative workplace photograph.

Both logo files were pixel-extracted from the supplied screenshots and are **raster, not
vector**. They are correct in colour and shape but will soften above ~320px wide. Ask Linko
for the SVG.

---

## Open questions / flags for the user

1. **Typeface substitution.** Linko's production face is a proprietary neo-grotesque
   (Helvetica/Aeonik lineage). The system currently loads **Archivo** from Google Fonts as
   the nearest available match. Please send the real webfont files (woff2) and I will swap
   `tokens/fonts.css` to `@font-face` rules.
2. **Logo files.** Raster extractions stand in for the real SVG lockup and mark.
3. **Service and industry illustrations** and **partner logos** are missing — components
   degrade gracefully but the kit looks under-dressed without them.
4. **Measurements** (spacing, radii, type sizes) are estimates from screenshots. A Figma
   file or the site's stylesheet would let me replace guesses with exact values.
5. **Unseen surfaces.** Blog index, blog article, case-study detail, privacy/T&C and any
   mobile breakpoint were not in the sources, so no screens were invented for them.
