/* @ds-bundle: {"format":4,"namespace":"LinkoDesignSystem_97b06d","components":[{"name":"RingMotif","sourcePath":"components/brand/RingMotif.jsx"},{"name":"CaseCard","sourcePath":"components/content/CaseCard.jsx"},{"name":"IndustryCard","sourcePath":"components/content/IndustryCard.jsx"},{"name":"PartnerTile","sourcePath":"components/content/PartnerTile.jsx"},{"name":"SolutionCard","sourcePath":"components/content/SolutionCard.jsx"},{"name":"StatBlock","sourcePath":"components/content/StatBlock.jsx"},{"name":"TimelineCard","sourcePath":"components/content/TimelineCard.jsx"},{"name":"ArrowButton","sourcePath":"components/core/ArrowButton.jsx"},{"name":"ArrowLink","sourcePath":"components/core/ArrowLink.jsx"},{"name":"Button","sourcePath":"components/core/Button.jsx"},{"name":"Chip","sourcePath":"components/core/Chip.jsx"},{"name":"LangToggle","sourcePath":"components/core/LangToggle.jsx"},{"name":"Footer","sourcePath":"components/layout/Footer.jsx"},{"name":"NavBar","sourcePath":"components/layout/NavBar.jsx"},{"name":"SectionHeading","sourcePath":"components/layout/SectionHeading.jsx"}],"sourceHashes":{"components/brand/RingMotif.jsx":"4e940ad2d30d","components/content/CaseCard.jsx":"0a42e273df7a","components/content/IndustryCard.jsx":"772a04b1e9cc","components/content/PartnerTile.jsx":"5eedb3dfe919","components/content/SolutionCard.jsx":"8ba1654be818","components/content/StatBlock.jsx":"a5df4c97f764","components/content/TimelineCard.jsx":"7d35c9eeeb41","components/core/ArrowButton.jsx":"c12e76bf3427","components/core/ArrowLink.jsx":"919854749a9c","components/core/Button.jsx":"4f3390057b27","components/core/Chip.jsx":"bf65016d29b9","components/core/LangToggle.jsx":"01f850ea6f81","components/layout/Footer.jsx":"60fc74ba49c7","components/layout/NavBar.jsx":"8418707601e9","components/layout/SectionHeading.jsx":"ce1007231d57","ui_kits/website/About.jsx":"cfef9a4ad8c8","ui_kits/website/App.jsx":"9147a458c0f8","ui_kits/website/Contact.jsx":"c86824d5fcb7","ui_kits/website/Home.jsx":"59a04605a553","ui_kits/website/Partners.jsx":"7fc70c8ba4f4","ui_kits/website/Solutions.jsx":"a30228175b83","ui_kits/website/copy.js":"995c8d48e9e6"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.LinkoDesignSystem_97b06d = window.LinkoDesignSystem_97b06d || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/brand/RingMotif.jsx
try { (() => {
function RingMotif({
  columns = 3,
  rows = 2,
  size = 220,
  gap = -18,
  color = "var(--green-400)",
  accentColor = "var(--lime-300)",
  accentIndex = 1,
  strokeWidth = 2,
  style
}) {
  const cells = Array.from({
    length: columns * rows
  });
  return /*#__PURE__*/React.createElement("div", {
    "aria-hidden": "true",
    style: {
      display: "grid",
      gridTemplateColumns: `repeat(${columns},${size}px)`,
      gap: `${gap}px`,
      justifyContent: "center",
      ...style
    }
  }, cells.map((_, i) => /*#__PURE__*/React.createElement("span", {
    key: i,
    style: {
      width: size,
      height: size,
      borderRadius: "var(--radius-circle)",
      border: `${strokeWidth}px solid ${i === accentIndex ? accentColor : color}`,
      display: "block"
    }
  })));
}
Object.assign(__ds_scope, { RingMotif });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/brand/RingMotif.jsx", error: String((e && e.message) || e) }); }

// components/content/IndustryCard.jsx
try { (() => {
function IndustryCard({
  name,
  description,
  iconSrc,
  style
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-4)",
      fontFamily: "var(--font-sans)",
      ...style
    }
  }, iconSrc ? /*#__PURE__*/React.createElement("img", {
    src: iconSrc,
    alt: "",
    style: {
      width: "56px",
      height: "56px",
      objectFit: "contain"
    }
  }) : /*#__PURE__*/React.createElement("span", {
    style: {
      width: "56px",
      height: "56px",
      borderRadius: "var(--radius-circle)",
      border: "2px solid var(--border-brand-soft)"
    }
  }), /*#__PURE__*/React.createElement("h3", {
    style: {
      margin: 0,
      fontSize: "var(--fs-heading-s)",
      fontWeight: "var(--fw-medium)",
      color: "var(--text-heading)"
    }
  }, name), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: "var(--type-body)",
      color: "var(--text-body)",
      maxWidth: "34ch"
    }
  }, description));
}
Object.assign(__ds_scope, { IndustryCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/content/IndustryCard.jsx", error: String((e && e.message) || e) }); }

// components/content/PartnerTile.jsx
try { (() => {
function PartnerTile({
  name,
  logoSrc,
  selected = false,
  onClick,
  style
}) {
  const [hover, setHover] = React.useState(false);
  return /*#__PURE__*/React.createElement("button", {
    onClick: onClick,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      gap: "var(--space-3)",
      background: "var(--surface-card)",
      border: selected ? "1px solid var(--border-brand)" : "1px solid var(--border-subtle)",
      borderRadius: "var(--radius-m)",
      padding: "var(--space-8)",
      cursor: "pointer",
      minHeight: "132px",
      boxShadow: hover ? "var(--shadow-card)" : "none",
      transition: "var(--transition-control),box-shadow var(--dur-base) var(--ease-standard)",
      fontFamily: "var(--font-sans)",
      ...style
    }
  }, logoSrc ? /*#__PURE__*/React.createElement("img", {
    src: logoSrc,
    alt: name,
    style: {
      maxHeight: "34px",
      maxWidth: "150px",
      objectFit: "contain"
    }
  }) : /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: "var(--fs-heading-s)",
      color: "var(--text-heading)"
    }
  }, name), logoSrc ? /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: "var(--fs-caption)",
      color: "var(--text-muted)"
    }
  }, name) : null);
}
Object.assign(__ds_scope, { PartnerTile });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/content/PartnerTile.jsx", error: String((e && e.message) || e) }); }

// components/content/SolutionCard.jsx
try { (() => {
function SolutionCard({
  title,
  iconSrc,
  description,
  href,
  onClick,
  style
}) {
  const [hover, setHover] = React.useState(false);
  return /*#__PURE__*/React.createElement("a", {
    href: href,
    onClick: onClick,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-6)",
      textDecoration: "none",
      background: "var(--surface-card)",
      borderRadius: "var(--radius-l)",
      padding: "var(--card-padding)",
      boxShadow: hover ? "var(--shadow-raised)" : "var(--shadow-card)",
      transform: hover ? "translateY(-4px)" : "none",
      transition: "box-shadow var(--dur-base) var(--ease-standard),transform var(--dur-base) var(--ease-out)",
      fontFamily: "var(--font-sans)",
      ...style
    }
  }, iconSrc ? /*#__PURE__*/React.createElement("img", {
    src: iconSrc,
    alt: "",
    style: {
      width: "64px",
      height: "64px",
      objectFit: "contain"
    }
  }) : /*#__PURE__*/React.createElement("span", {
    style: {
      width: "64px",
      height: "64px",
      borderRadius: "var(--radius-circle)",
      border: "2px solid var(--border-brand-soft)",
      display: "block"
    }
  }), /*#__PURE__*/React.createElement("h3", {
    style: {
      margin: 0,
      font: "var(--fw-regular) var(--fs-heading-m)/var(--lh-heading-m) var(--font-display)",
      letterSpacing: "var(--tracking-heading)",
      color: "var(--text-heading)"
    }
  }, title), description ? /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: "var(--type-body)",
      color: "var(--text-body)"
    }
  }, description) : null);
}
Object.assign(__ds_scope, { SolutionCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/content/SolutionCard.jsx", error: String((e && e.message) || e) }); }

// components/content/StatBlock.jsx
try { (() => {
function StatBlock({
  value,
  label,
  tone = "brand",
  align = "left",
  style
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-2)",
      textAlign: align,
      fontFamily: "var(--font-sans)",
      ...style
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: "var(--fw-regular) var(--fs-display-l)/var(--lh-display-l) var(--font-display)",
      letterSpacing: "var(--tracking-display)",
      color: tone === "brand" ? "var(--text-brand)" : "var(--text-heading)"
    }
  }, value), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: "var(--fs-body-m)",
      color: "var(--text-body)",
      maxWidth: "18ch"
    }
  }, label));
}
Object.assign(__ds_scope, { StatBlock });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/content/StatBlock.jsx", error: String((e && e.message) || e) }); }

// components/content/TimelineCard.jsx
try { (() => {
function TimelineCard({
  year,
  body,
  mediaSrc,
  mediaSlot,
  style
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "1fr 1fr",
      borderRadius: "var(--radius-l)",
      overflow: "hidden",
      background: "var(--surface-card)",
      boxShadow: "var(--shadow-card)",
      minHeight: "420px",
      fontFamily: "var(--font-sans)",
      ...style
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "var(--space-10)"
    }
  }, mediaSlot || (mediaSrc ? /*#__PURE__*/React.createElement("img", {
    src: mediaSrc,
    alt: "",
    style: {
      maxWidth: "100%",
      maxHeight: "300px",
      objectFit: "contain"
    }
  }) : null)), /*#__PURE__*/React.createElement("div", {
    style: {
      background: "var(--surface-brand)",
      color: "var(--text-on-brand)",
      padding: "var(--space-10)",
      display: "flex",
      flexDirection: "column",
      justifyContent: "space-between",
      gap: "var(--space-10)"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: "var(--fw-regular) var(--fs-display-m)/var(--lh-display-m) var(--font-display)",
      letterSpacing: "var(--tracking-display)"
    }
  }, year), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: "var(--fs-body-l)",
      lineHeight: "var(--lh-body-l)",
      maxWidth: "46ch"
    }
  }, body)));
}
Object.assign(__ds_scope, { TimelineCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/content/TimelineCard.jsx", error: String((e && e.message) || e) }); }

// components/core/ArrowButton.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const ArrowGlyph = ({
  size = 18,
  strokeWidth = 2
}) => /*#__PURE__*/React.createElement("svg", {
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: strokeWidth,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  "aria-hidden": "true"
}, /*#__PURE__*/React.createElement("path", {
  d: "M4 12h15M13 6l6 6-6 6"
}));
function ArrowButton({
  variant = "primary",
  size = 52,
  direction = "right",
  disabled = false,
  onClick,
  href,
  "aria-label": ariaLabel = "Continue",
  style,
  ...rest
}) {
  const [hover, setHover] = React.useState(false);
  const [down, setDown] = React.useState(false);
  const palette = {
    primary: {
      background: "var(--surface-brand)",
      color: "var(--text-on-brand)",
      border: "1px solid transparent"
    },
    dark: {
      background: "var(--surface-ink)",
      color: "var(--text-on-ink)",
      border: "1px solid transparent"
    },
    outline: {
      background: "transparent",
      color: "var(--text-brand)",
      border: "1px solid var(--border-brand)"
    }
  }[variant];
  const hoverBg = {
    primary: "var(--green-600)",
    dark: "var(--ink-700)",
    outline: "var(--green-100)"
  }[variant];
  const rotate = {
    right: 0,
    left: 180,
    up: -90,
    down: 90
  }[direction];
  const Tag = href ? "a" : "button";
  return /*#__PURE__*/React.createElement(Tag, _extends({
    href: href,
    onClick: onClick,
    "aria-label": ariaLabel,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => {
      setHover(false);
      setDown(false);
    },
    onMouseDown: () => setDown(true),
    onMouseUp: () => setDown(false),
    style: {
      width: size,
      height: size,
      borderRadius: "var(--radius-circle)",
      display: "inline-flex",
      alignItems: "center",
      justifyContent: "center",
      cursor: "pointer",
      transition: "var(--transition-control)",
      ...palette,
      background: hover && !disabled ? hoverBg : palette.background,
      transform: down && !disabled ? "scale(var(--press-scale))" : "none",
      opacity: disabled ? 0.45 : 1,
      pointerEvents: disabled ? "none" : "auto",
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("span", {
    style: {
      display: "inline-flex",
      transform: `rotate(${rotate}deg)`
    }
  }, /*#__PURE__*/React.createElement(ArrowGlyph, {
    size: Math.round(size * 0.42)
  })));
}
Object.assign(__ds_scope, { ArrowButton });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/ArrowButton.jsx", error: String((e && e.message) || e) }); }

// components/core/ArrowLink.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const ArrowGlyph = ({
  size = 18,
  strokeWidth = 2
}) => /*#__PURE__*/React.createElement("svg", {
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: strokeWidth,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  "aria-hidden": "true"
}, /*#__PURE__*/React.createElement("path", {
  d: "M4 12h15M13 6l6 6-6 6"
}));
function ArrowLink({
  children,
  href = "#",
  tone = "brand",
  onClick,
  style,
  ...rest
}) {
  const [hover, setHover] = React.useState(false);
  const color = tone === "ink" ? "var(--text-heading)" : "var(--text-brand)";
  return /*#__PURE__*/React.createElement("a", _extends({
    href: href,
    onClick: onClick,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
      display: "inline-flex",
      alignItems: "center",
      gap: hover ? "14px" : "10px",
      color,
      fontFamily: "var(--font-sans)",
      fontSize: "var(--fs-body-m)",
      textDecoration: "none",
      transition: "gap var(--dur-base) var(--ease-out),opacity var(--dur-base) var(--ease-standard)",
      opacity: hover ? 0.75 : 1,
      ...style
    }
  }, rest), children, /*#__PURE__*/React.createElement(ArrowGlyph, {
    size: 18
  }));
}
Object.assign(__ds_scope, { ArrowLink });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/ArrowLink.jsx", error: String((e && e.message) || e) }); }

// components/content/CaseCard.jsx
try { (() => {
function CaseCard({
  title,
  imageSrc,
  bullets = [],
  linkLabel = "Conoce más",
  href,
  onClick,
  style
}) {
  return /*#__PURE__*/React.createElement("article", {
    style: {
      display: "flex",
      flexDirection: "column",
      background: "var(--surface-card)",
      borderRadius: "var(--radius-l)",
      overflow: "hidden",
      boxShadow: "var(--shadow-card)",
      fontFamily: "var(--font-sans)",
      ...style
    }
  }, imageSrc ? /*#__PURE__*/React.createElement("img", {
    src: imageSrc,
    alt: "",
    style: {
      width: "100%",
      height: "220px",
      objectFit: "cover",
      display: "block"
    }
  }) : null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-5)",
      padding: "var(--card-padding)"
    }
  }, /*#__PURE__*/React.createElement("h3", {
    style: {
      margin: 0,
      font: "var(--fw-regular) var(--fs-heading-m)/var(--lh-heading-m) var(--font-display)",
      letterSpacing: "var(--tracking-heading)",
      color: "var(--text-heading)"
    }
  }, title), /*#__PURE__*/React.createElement("ul", {
    style: {
      margin: 0,
      paddingLeft: "1.1em",
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-2)",
      color: "var(--text-body)",
      fontSize: "var(--fs-body-m)",
      lineHeight: "var(--lh-body-m)"
    }
  }, bullets.map((b, i) => /*#__PURE__*/React.createElement("li", {
    key: i
  }, b))), /*#__PURE__*/React.createElement(__ds_scope.ArrowLink, {
    href: href,
    onClick: onClick
  }, linkLabel)));
}
Object.assign(__ds_scope, { CaseCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/content/CaseCard.jsx", error: String((e && e.message) || e) }); }

// components/core/Button.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const ArrowGlyph = ({
  size = 18,
  strokeWidth = 2
}) => /*#__PURE__*/React.createElement("svg", {
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: strokeWidth,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  "aria-hidden": "true"
}, /*#__PURE__*/React.createElement("path", {
  d: "M4 12h15M13 6l6 6-6 6"
}));
const base = {
  display: "inline-flex",
  alignItems: "center",
  gap: "10px",
  fontFamily: "var(--font-sans)",
  fontWeight: "var(--fw-regular)",
  borderRadius: "var(--radius-pill)",
  border: "1px solid transparent",
  cursor: "pointer",
  textDecoration: "none",
  whiteSpace: "nowrap",
  transition: "var(--transition-control)"
};
const sizes = {
  m: {
    padding: "12px 22px",
    fontSize: "var(--fs-label)"
  },
  l: {
    padding: "16px 30px",
    fontSize: "var(--fs-body-l)"
  }
};
const variants = {
  primary: {
    background: "var(--surface-brand)",
    color: "var(--text-on-brand)"
  },
  secondary: {
    background: "transparent",
    color: "var(--text-brand)",
    borderColor: "var(--border-brand)"
  },
  dark: {
    background: "var(--surface-ink)",
    color: "var(--text-on-ink)"
  },
  ghost: {
    background: "transparent",
    color: "var(--text-heading)"
  }
};
const hovers = {
  primary: {
    background: "var(--green-600)"
  },
  secondary: {
    background: "var(--green-100)"
  },
  dark: {
    background: "var(--ink-700)"
  },
  ghost: {
    background: "var(--neutral-100)"
  }
};
function Button({
  children,
  variant = "primary",
  size = "m",
  withArrow = false,
  disabled = false,
  href,
  onClick,
  style,
  ...rest
}) {
  const [hover, setHover] = React.useState(false);
  const [down, setDown] = React.useState(false);
  const Tag = href ? "a" : "button";
  const css = {
    ...base,
    ...sizes[size],
    ...variants[variant],
    ...(hover && !disabled ? hovers[variant] : null),
    transform: down && !disabled ? "scale(var(--press-scale))" : "none",
    opacity: disabled ? 0.45 : 1,
    pointerEvents: disabled ? "none" : "auto",
    ...style
  };
  return /*#__PURE__*/React.createElement(Tag, _extends({
    href: href,
    onClick: onClick,
    disabled: !href && disabled ? true : undefined,
    style: css,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => {
      setHover(false);
      setDown(false);
    },
    onMouseDown: () => setDown(true),
    onMouseUp: () => setDown(false)
  }, rest), /*#__PURE__*/React.createElement("span", null, children), withArrow ? /*#__PURE__*/React.createElement(ArrowGlyph, {
    size: size === "l" ? 20 : 18
  }) : null);
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Button.jsx", error: String((e && e.message) || e) }); }

// components/core/Chip.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function Chip({
  children,
  tone = "brand",
  size = "m",
  style,
  ...rest
}) {
  const tones = {
    brand: {
      background: "var(--surface-brand)",
      color: "var(--text-on-brand)"
    },
    ink: {
      background: "var(--surface-ink)",
      color: "var(--text-on-ink)"
    },
    soft: {
      background: "var(--green-100)",
      color: "var(--ink-900)"
    },
    outline: {
      background: "transparent",
      color: "var(--text-brand)",
      border: "1px solid var(--border-brand)"
    }
  };
  const sizes = {
    s: {
      padding: "6px 14px",
      fontSize: "var(--fs-caption)"
    },
    m: {
      padding: "10px 24px",
      fontSize: "var(--fs-label)"
    }
  };
  return /*#__PURE__*/React.createElement("span", _extends({
    style: {
      display: "inline-flex",
      alignItems: "center",
      borderRadius: "var(--radius-pill)",
      fontFamily: "var(--font-sans)",
      lineHeight: 1.2,
      ...tones[tone],
      ...sizes[size],
      ...style
    }
  }, rest), children);
}
Object.assign(__ds_scope, { Chip });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Chip.jsx", error: String((e && e.message) || e) }); }

// components/core/LangToggle.jsx
try { (() => {
function LangToggle({
  value = "es",
  onChange,
  options = [{
    id: "es",
    label: "Esp"
  }, {
    id: "en",
    label: "Eng"
  }],
  style
}) {
  return /*#__PURE__*/React.createElement("div", {
    role: "group",
    "aria-label": "Idioma",
    style: {
      display: "inline-flex",
      alignItems: "center",
      border: "1px solid var(--border-subtle)",
      borderRadius: "var(--radius-pill)",
      background: "var(--neutral-0)",
      padding: 0,
      ...style
    }
  }, options.map(o => {
    const active = o.id === value;
    return /*#__PURE__*/React.createElement("button", {
      key: o.id,
      onClick: () => onChange && onChange(o.id),
      "aria-pressed": active,
      style: {
        appearance: "none",
        border: "none",
        cursor: "pointer",
        fontFamily: "var(--font-sans)",
        fontSize: "var(--fs-label)",
        padding: "10px 20px",
        borderRadius: "var(--radius-pill)",
        background: active ? "var(--surface-ink)" : "transparent",
        color: active ? "var(--text-on-ink)" : "var(--text-heading)",
        transition: "var(--transition-control)"
      }
    }, o.label);
  }));
}
Object.assign(__ds_scope, { LangToggle });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/LangToggle.jsx", error: String((e && e.message) || e) }); }

// components/layout/Footer.jsx
try { (() => {
function Footer({
  markSrc,
  tagline = "Take the next step, simplified solutions.",
  columns = [],
  contactHeading = "Contacto",
  contactBody = "Nuestro equipo de expertos está listo para asistirte en todo momento y llevar tu tecnología al siguiente nivel.",
  contactCtaLabel = "Contáctanos",
  onContact,
  legal = "© Linko 2026",
  legalLinks = [],
  onNavigate,
  style
}) {
  return /*#__PURE__*/React.createElement("footer", {
    style: {
      background: "var(--surface-chrome)",
      padding: "var(--space-24) var(--page-margin) var(--space-12)",
      fontFamily: "var(--font-sans)",
      color: "var(--text-heading)",
      ...style
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: "var(--container-max)",
      margin: "0 auto",
      display: "grid",
      gridTemplateColumns: "1.2fr 1fr 1.4fr",
      gap: "var(--space-16)"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-12)"
    }
  }, /*#__PURE__*/React.createElement("img", {
    src: markSrc,
    alt: "Linko",
    style: {
      height: "70px",
      width: "auto",
      alignSelf: "flex-start"
    }
  }), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: "var(--type-section)",
      letterSpacing: "var(--tracking-display)",
      maxWidth: "9ch"
    }
  }, tagline)), columns.map(col => /*#__PURE__*/React.createElement("div", {
    key: col.title,
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-6)"
    }
  }, /*#__PURE__*/React.createElement("h3", {
    style: {
      margin: 0,
      color: "var(--text-brand)",
      fontSize: "var(--fs-heading-s)",
      fontWeight: "var(--fw-regular)"
    }
  }, col.title), /*#__PURE__*/React.createElement("ul", {
    style: {
      listStyle: "none",
      margin: 0,
      padding: 0,
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-2)"
    }
  }, col.links.map(l => /*#__PURE__*/React.createElement("li", {
    key: l.href
  }, /*#__PURE__*/React.createElement("a", {
    href: l.href,
    onClick: e => {
      e.preventDefault();
      onNavigate && onNavigate(l.href);
    },
    style: {
      color: "var(--text-heading)",
      textDecoration: "none",
      fontSize: "var(--fs-body-l)"
    }
  }, l.label)))))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-6)"
    }
  }, /*#__PURE__*/React.createElement("h3", {
    style: {
      margin: 0,
      color: "var(--text-brand)",
      fontSize: "var(--fs-heading-s)",
      fontWeight: "var(--fw-regular)"
    }
  }, contactHeading), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: "var(--fs-body-l)",
      lineHeight: "var(--lh-body-l)",
      maxWidth: "42ch"
    }
  }, contactBody), /*#__PURE__*/React.createElement(__ds_scope.ArrowLink, {
    tone: "ink",
    onClick: e => {
      e.preventDefault();
      onContact && onContact();
    }
  }, contactCtaLabel))), /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: "var(--container-max)",
      margin: "var(--space-16) auto 0",
      paddingTop: "var(--space-6)",
      borderTop: "1px solid var(--border-subtle)",
      display: "flex",
      alignItems: "center",
      gap: "var(--space-4)",
      fontSize: "var(--fs-body-s)",
      color: "var(--text-body)"
    }
  }, /*#__PURE__*/React.createElement("span", null, legal), legalLinks.map(l => /*#__PURE__*/React.createElement(React.Fragment, {
    key: l.href
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true"
  }, "|"), /*#__PURE__*/React.createElement("a", {
    href: l.href,
    style: {
      color: "var(--text-body)",
      textDecoration: "none"
    }
  }, l.label)))));
}
Object.assign(__ds_scope, { Footer });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/layout/Footer.jsx", error: String((e && e.message) || e) }); }

// components/layout/NavBar.jsx
try { (() => {
function NavBar({
  logoSrc,
  links = [],
  activeHref,
  lang = "es",
  onLangChange,
  ctaLabel = "Contáctanos",
  onCta,
  onNavigate,
  floating = true,
  translucent = false,
  style
}) {
  return /*#__PURE__*/React.createElement("nav", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: "var(--space-8)",
      padding: "10px 10px 10px 28px",
      borderRadius: "var(--radius-pill)",
      background: translucent ? "var(--scrim-nav)" : "var(--surface-chrome)",
      backdropFilter: translucent ? "var(--blur-chrome)" : "none",
      WebkitBackdropFilter: translucent ? "var(--blur-chrome)" : "none",
      boxShadow: floating ? "var(--shadow-nav)" : "none",
      fontFamily: "var(--font-sans)",
      ...style
    }
  }, /*#__PURE__*/React.createElement("a", {
    href: "#",
    onClick: e => {
      e.preventDefault();
      onNavigate && onNavigate("/");
    },
    style: {
      display: "flex",
      alignItems: "center",
      flexShrink: 0
    }
  }, /*#__PURE__*/React.createElement("img", {
    src: logoSrc,
    alt: "Linko",
    style: {
      height: "34px",
      display: "block"
    }
  })), /*#__PURE__*/React.createElement("ul", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: "var(--space-10)",
      listStyle: "none",
      margin: "0 auto",
      padding: 0
    }
  }, links.map(l => /*#__PURE__*/React.createElement("li", {
    key: l.href
  }, /*#__PURE__*/React.createElement("a", {
    href: l.href,
    onClick: e => {
      e.preventDefault();
      onNavigate && onNavigate(l.href);
    },
    style: {
      textDecoration: "none",
      fontSize: "var(--fs-body-m)",
      color: l.href === activeHref ? "var(--text-brand)" : "var(--text-heading)",
      transition: "var(--transition-control)"
    }
  }, l.label)))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: "var(--space-4)",
      flexShrink: 0
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.LangToggle, {
    value: lang,
    onChange: onLangChange
  }), /*#__PURE__*/React.createElement(__ds_scope.Button, {
    variant: "primary",
    onClick: onCta
  }, ctaLabel), /*#__PURE__*/React.createElement(__ds_scope.ArrowButton, {
    variant: "primary",
    size: 52,
    "aria-label": ctaLabel,
    onClick: onCta
  })));
}
Object.assign(__ds_scope, { NavBar });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/layout/NavBar.jsx", error: String((e && e.message) || e) }); }

// components/layout/SectionHeading.jsx
try { (() => {
function SectionHeading({
  eyebrow,
  title,
  body,
  align = "left",
  size = "m",
  style
}) {
  const font = size === "l" ? "var(--fw-regular) var(--fs-display-l)/var(--lh-display-l) var(--font-display)" : "var(--type-section)";
  return /*#__PURE__*/React.createElement("header", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-4)",
      textAlign: align,
      alignItems: align === "center" ? "center" : "flex-start",
      fontFamily: "var(--font-sans)",
      ...style
    }
  }, eyebrow ? /*#__PURE__*/React.createElement("span", {
    style: {
      color: "var(--text-brand)",
      fontSize: "var(--fs-body-m)"
    }
  }, eyebrow) : null, /*#__PURE__*/React.createElement("h2", {
    style: {
      margin: 0,
      font,
      letterSpacing: "var(--tracking-display)",
      color: "var(--text-heading)",
      maxWidth: "22ch"
    }
  }, title), body ? /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: "var(--type-body)",
      color: "var(--text-body)",
      maxWidth: "60ch"
    }
  }, body) : null);
}
Object.assign(__ds_scope, { SectionHeading });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/layout/SectionHeading.jsx", error: String((e && e.message) || e) }); }

// ui_kits/website/About.jsx
try { (() => {
const {
  Chip,
  TimelineCard,
  SectionHeading,
  RingMotif
} = window.LinkoDesignSystem_97b06d;
function About({
  t
}) {
  const [active, setActive] = React.useState(0);
  const [year, body] = t.milestones[active];
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--section-y)",
      paddingBottom: "var(--section-y)"
    }
  }, /*#__PURE__*/React.createElement(Section, {
    style: {
      paddingTop: "190px",
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-12)"
    }
  }, /*#__PURE__*/React.createElement(SectionHeading, {
    title: t.historyTitle,
    size: "l"
  }), /*#__PURE__*/React.createElement(TimelineCard, {
    year: year,
    body: body,
    mediaSlot: /*#__PURE__*/React.createElement(RingMotif, {
      columns: 2,
      rows: 1,
      size: 130,
      accentIndex: 0
    })
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: "var(--space-2)"
    }
  }, t.milestones.map(([y], i) => /*#__PURE__*/React.createElement(React.Fragment, {
    key: y
  }, /*#__PURE__*/React.createElement("button", {
    onClick: () => setActive(i),
    style: {
      background: "none",
      border: "none",
      padding: 0,
      cursor: "pointer"
    }
  }, /*#__PURE__*/React.createElement(Chip, {
    tone: i === active ? "brand" : "ink"
  }, y)), i < t.milestones.length - 1 ? /*#__PURE__*/React.createElement("span", {
    style: {
      flex: 1,
      height: "1px",
      background: "var(--border-subtle)"
    }
  }) : null)))), /*#__PURE__*/React.createElement(Section, null, /*#__PURE__*/React.createElement("div", {
    style: {
      position: "relative",
      borderRadius: "var(--radius-xl)",
      overflow: "hidden",
      height: "460px"
    }
  }, /*#__PURE__*/React.createElement("img", {
    src: "../../assets/photo-team.jpg",
    alt: "",
    style: {
      width: "100%",
      height: "100%",
      objectFit: "cover",
      display: "block"
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      position: "absolute",
      left: "56px",
      top: "56px",
      background: "var(--surface-card)",
      borderRadius: "var(--radius-s)",
      padding: "var(--space-8)",
      maxWidth: "380px",
      fontSize: "var(--fs-body-m)",
      lineHeight: "var(--lh-body-m)",
      color: "var(--text-heading)"
    }
  }, t.teamCaption))));
}
Object.assign(window, {
  About
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/website/About.jsx", error: String((e && e.message) || e) }); }

// ui_kits/website/App.jsx
try { (() => {
const {
  NavBar,
  Footer
} = window.LinkoDesignSystem_97b06d;
function App() {
  const [lang, setLang] = React.useState("es");
  const [route, setRoute] = React.useState("/");
  const [partner, setPartner] = React.useState("UiPath");
  const t = window.LinkoCopy[lang];
  const go = href => {
    setRoute(href);
    window.scrollTo({
      top: 0
    });
  };
  const screens = {
    "/": /*#__PURE__*/React.createElement(Home, {
      t: t,
      go: go,
      selectedPartner: partner,
      onSelectPartner: setPartner
    }),
    "/nosotros": /*#__PURE__*/React.createElement(About, {
      t: t
    }),
    "/soluciones": /*#__PURE__*/React.createElement(Solutions, {
      t: t,
      go: go
    }),
    "/tecnologia": /*#__PURE__*/React.createElement(Partners, {
      t: t,
      selectedPartner: partner,
      onSelectPartner: setPartner
    }),
    "/blog": /*#__PURE__*/React.createElement(Solutions, {
      t: t,
      go: go
    }),
    "/contacto": /*#__PURE__*/React.createElement(Contact, {
      t: t
    })
  };
  return /*#__PURE__*/React.createElement("div", {
    style: {
      background: "var(--surface-page)",
      minHeight: "100vh"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      position: "fixed",
      top: "var(--space-5)",
      left: "var(--page-margin)",
      right: "var(--page-margin)",
      zIndex: 10
    }
  }, /*#__PURE__*/React.createElement(NavBar, {
    logoSrc: "../../assets/linko-logo.png",
    links: t.nav,
    activeHref: route,
    lang: lang,
    onLangChange: setLang,
    ctaLabel: t.cta,
    onCta: () => go("/contacto"),
    onNavigate: go
  })), screens[route], /*#__PURE__*/React.createElement(Footer, {
    markSrc: "../../assets/linko-mark.png",
    tagline: t.footerTagline,
    onNavigate: go,
    onContact: () => go("/contacto"),
    columns: [{
      title: t.footerSite,
      links: t.nav
    }],
    contactHeading: t.footerContact,
    contactBody: t.footerBody,
    contactCtaLabel: t.cta,
    legal: t.legal,
    legalLinks: [{
      label: t.privacy,
      href: "#"
    }, {
      label: t.terms,
      href: "#"
    }]
  }));
}
ReactDOM.createRoot(document.getElementById("root")).render(/*#__PURE__*/React.createElement(App, null));
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/website/App.jsx", error: String((e && e.message) || e) }); }

// ui_kits/website/Contact.jsx
try { (() => {
const {
  SectionHeading,
  Button
} = window.LinkoDesignSystem_97b06d;
function Field({
  label,
  type = "text",
  value,
  onChange,
  multiline
}) {
  const shared = {
    width: "100%",
    boxSizing: "border-box",
    padding: "14px 18px",
    borderRadius: multiline ? "var(--radius-s)" : "var(--radius-pill)",
    border: "1px solid var(--border-subtle)",
    background: "var(--surface-card)",
    fontFamily: "var(--font-sans)",
    fontSize: "var(--fs-body-m)",
    color: "var(--text-heading)",
    outline: "none"
  };
  return /*#__PURE__*/React.createElement("label", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-2)"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: "var(--fs-body-s)",
      color: "var(--text-body)"
    }
  }, label), multiline ? /*#__PURE__*/React.createElement("textarea", {
    rows: 4,
    value: value,
    onChange: e => onChange(e.target.value),
    style: {
      ...shared,
      resize: "vertical"
    }
  }) : /*#__PURE__*/React.createElement("input", {
    type: type,
    value: value,
    onChange: e => onChange(e.target.value),
    style: shared
  }));
}
function Contact({
  t
}) {
  const [form, setForm] = React.useState({
    name: "",
    email: "",
    company: "",
    message: ""
  });
  const [sent, setSent] = React.useState(false);
  const set = k => v => setForm(s => ({
    ...s,
    [k]: v
  }));
  const valid = form.name.trim() && /@/.test(form.email);
  return /*#__PURE__*/React.createElement("div", {
    style: {
      paddingBottom: "var(--section-y)"
    }
  }, /*#__PURE__*/React.createElement(Section, {
    style: {
      paddingTop: "190px",
      display: "grid",
      gridTemplateColumns: "1fr 1fr",
      gap: "var(--space-16)",
      alignItems: "start"
    }
  }, /*#__PURE__*/React.createElement(SectionHeading, {
    title: t.contactTitle,
    body: t.contactBody,
    size: "l"
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      background: "var(--surface-card)",
      borderRadius: "var(--radius-l)",
      padding: "var(--space-10)",
      boxShadow: "var(--shadow-card)",
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-5)"
    }
  }, sent ? /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: "var(--fs-body-l)",
      color: "var(--text-brand)"
    }
  }, t.formDone) : /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(Field, {
    label: t.formLabels.name,
    value: form.name,
    onChange: set("name")
  }), /*#__PURE__*/React.createElement(Field, {
    label: t.formLabels.email,
    type: "email",
    value: form.email,
    onChange: set("email")
  }), /*#__PURE__*/React.createElement(Field, {
    label: t.formLabels.company,
    value: form.company,
    onChange: set("company")
  }), /*#__PURE__*/React.createElement(Field, {
    label: t.formLabels.message,
    multiline: true,
    value: form.message,
    onChange: set("message")
  }), /*#__PURE__*/React.createElement(Button, {
    variant: "primary",
    size: "l",
    withArrow: true,
    disabled: !valid,
    onClick: () => setSent(true)
  }, t.formSubmit)))));
}
Object.assign(window, {
  Contact
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/website/Contact.jsx", error: String((e && e.message) || e) }); }

// ui_kits/website/Home.jsx
try { (() => {
const {
  Button,
  ArrowLink,
  RingMotif,
  SectionHeading,
  StatBlock,
  SolutionCard,
  CaseCard,
  IndustryCard,
  PartnerTile
} = window.LinkoDesignSystem_97b06d;
function Section({
  children,
  style
}) {
  return /*#__PURE__*/React.createElement("section", {
    style: {
      maxWidth: "var(--container-max)",
      margin: "0 auto",
      padding: "0 var(--page-margin)",
      ...style
    }
  }, children);
}
function Home({
  t,
  go,
  onSelectPartner,
  selectedPartner
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--section-y)",
      paddingBottom: "var(--section-y)"
    }
  }, /*#__PURE__*/React.createElement(Section, {
    style: {
      paddingTop: "190px",
      display: "grid",
      gridTemplateColumns: "1fr 1fr",
      gap: "var(--space-16)",
      alignItems: "center",
      minHeight: "620px"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-10)"
    }
  }, /*#__PURE__*/React.createElement("h1", {
    style: {
      margin: 0,
      font: "var(--type-hero)",
      letterSpacing: "var(--tracking-display)",
      color: "var(--text-heading)",
      maxWidth: "12ch"
    }
  }, t.heroTitle), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      gap: "var(--space-4)"
    }
  }, /*#__PURE__*/React.createElement(Button, {
    variant: "primary",
    withArrow: true,
    onClick: () => go("/contacto")
  }, t.cta), /*#__PURE__*/React.createElement(Button, {
    variant: "secondary",
    withArrow: true,
    onClick: () => go("/soluciones")
  }, t.heroSecondary))), /*#__PURE__*/React.createElement(RingMotif, {
    size: 210,
    style: {
      justifySelf: "center"
    }
  })), /*#__PURE__*/React.createElement(Section, {
    style: {
      display: "grid",
      gridTemplateColumns: "1fr 1fr",
      gap: "var(--space-16)",
      alignItems: "start"
    }
  }, /*#__PURE__*/React.createElement("h2", {
    style: {
      margin: 0,
      font: "var(--fw-regular) var(--fs-display-l)/var(--lh-display-l) var(--font-display)",
      letterSpacing: "var(--tracking-display)",
      color: "var(--text-heading)"
    }
  }, t.positioning), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: "var(--fs-body-l)",
      lineHeight: "var(--lh-body-l)",
      color: "var(--text-body)"
    }
  }, t.positioningBody)), /*#__PURE__*/React.createElement(Section, {
    style: {
      display: "grid",
      gridTemplateColumns: "repeat(5,1fr)",
      gap: "var(--space-8)"
    }
  }, t.stats.map(([v, l]) => /*#__PURE__*/React.createElement(StatBlock, {
    key: l,
    value: v,
    label: l
  }))), /*#__PURE__*/React.createElement(Section, {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-12)"
    }
  }, /*#__PURE__*/React.createElement(SectionHeading, {
    eyebrow: t.offerEyebrow,
    title: t.offerTitle
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "repeat(3,1fr)",
      gap: "var(--space-6)"
    }
  }, t.solutions.map(([title, desc]) => /*#__PURE__*/React.createElement(SolutionCard, {
    key: title,
    title: title,
    description: desc,
    onClick: e => {
      e.preventDefault();
      go("/soluciones");
    }
  })))), /*#__PURE__*/React.createElement(Section, {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-12)"
    }
  }, /*#__PURE__*/React.createElement(SectionHeading, {
    title: t.casesTitle,
    size: "l"
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "repeat(3,1fr)",
      gap: "var(--space-6)"
    }
  }, t.cases.map(([title, bullets], i) => /*#__PURE__*/React.createElement(CaseCard, {
    key: title,
    title: title,
    bullets: bullets,
    imageSrc: i === 0 ? "../../assets/photo-team.jpg" : undefined,
    onClick: e => e.preventDefault()
  })))), /*#__PURE__*/React.createElement(Section, {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-12)"
    }
  }, /*#__PURE__*/React.createElement(SectionHeading, {
    title: t.industriesTitle,
    body: t.industriesBody,
    size: "l"
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "repeat(4,1fr)",
      gap: "var(--space-10)"
    }
  }, t.industries.map(([name, desc]) => /*#__PURE__*/React.createElement(IndustryCard, {
    key: name,
    name: name,
    description: desc
  })))), /*#__PURE__*/React.createElement(Section, {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-12)"
    }
  }, /*#__PURE__*/React.createElement(SectionHeading, {
    title: t.partnersTitle,
    body: t.partnersBody,
    size: "l"
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "repeat(4,1fr)",
      gap: "var(--space-4)"
    }
  }, window.LinkoPartners.map(p => /*#__PURE__*/React.createElement(PartnerTile, {
    key: p,
    name: p,
    selected: p === selectedPartner,
    onClick: () => onSelectPartner(p)
  }))), /*#__PURE__*/React.createElement("div", {
    style: {
      background: "var(--surface-card)",
      borderRadius: "var(--radius-l)",
      padding: "var(--card-padding)",
      boxShadow: "var(--shadow-card)",
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-3)"
    }
  }, /*#__PURE__*/React.createElement("h3", {
    style: {
      margin: 0,
      fontSize: "var(--fs-heading-m)",
      fontWeight: "var(--fw-regular)",
      color: "var(--text-heading)"
    }
  }, selectedPartner), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      font: "var(--type-body)",
      color: "var(--text-body)",
      maxWidth: "70ch"
    }
  }, window.LinkoPartnerBlurbs[selectedPartner]), /*#__PURE__*/React.createElement(ArrowLink, {
    href: "#",
    onClick: e => e.preventDefault()
  }, "Website"))));
}
Object.assign(window, {
  Home,
  Section
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/website/Home.jsx", error: String((e && e.message) || e) }); }

// ui_kits/website/Partners.jsx
try { (() => {
const {
  SectionHeading,
  PartnerTile,
  ArrowLink
} = window.LinkoDesignSystem_97b06d;
function Partners({
  t,
  selectedPartner,
  onSelectPartner
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--section-y)",
      paddingBottom: "var(--section-y)"
    }
  }, /*#__PURE__*/React.createElement(Section, {
    style: {
      paddingTop: "190px",
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-12)"
    }
  }, /*#__PURE__*/React.createElement(SectionHeading, {
    title: t.partnersTitle,
    body: t.partnersBody,
    size: "l"
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "repeat(4,1fr)",
      gap: "var(--space-4)"
    }
  }, window.LinkoPartners.map(p => /*#__PURE__*/React.createElement(PartnerTile, {
    key: p,
    name: p,
    selected: p === selectedPartner,
    onClick: () => onSelectPartner(p)
  }))), /*#__PURE__*/React.createElement("div", {
    style: {
      background: "var(--surface-card)",
      borderRadius: "var(--radius-l)",
      padding: "var(--space-10)",
      boxShadow: "var(--shadow-card)",
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-4)"
    }
  }, /*#__PURE__*/React.createElement("h3", {
    style: {
      margin: 0,
      font: "var(--fw-regular) var(--fs-heading-l)/var(--lh-heading-l) var(--font-display)",
      letterSpacing: "var(--tracking-heading)",
      color: "var(--text-heading)"
    }
  }, selectedPartner), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: "var(--fs-body-l)",
      lineHeight: "var(--lh-body-l)",
      color: "var(--text-body)",
      maxWidth: "72ch"
    }
  }, window.LinkoPartnerBlurbs[selectedPartner]), /*#__PURE__*/React.createElement(ArrowLink, {
    href: "#",
    onClick: e => e.preventDefault()
  }, "Website"))));
}
Object.assign(window, {
  Partners
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/website/Partners.jsx", error: String((e && e.message) || e) }); }

// ui_kits/website/Solutions.jsx
try { (() => {
const {
  SectionHeading,
  SolutionCard,
  Button
} = window.LinkoDesignSystem_97b06d;
function Solutions({
  t,
  go
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "var(--section-y)",
      paddingBottom: "var(--section-y)"
    }
  }, /*#__PURE__*/React.createElement(Section, {
    style: {
      paddingTop: "190px",
      display: "flex",
      flexDirection: "column",
      gap: "var(--space-12)"
    }
  }, /*#__PURE__*/React.createElement(SectionHeading, {
    eyebrow: t.offerEyebrow,
    title: t.offerTitle,
    size: "l"
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "repeat(2,1fr)",
      gap: "var(--space-6)"
    }
  }, t.solutions.map(([title, desc]) => /*#__PURE__*/React.createElement(SolutionCard, {
    key: title,
    title: title,
    description: desc,
    onClick: e => e.preventDefault()
  }))), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement(Button, {
    variant: "primary",
    size: "l",
    withArrow: true,
    onClick: () => go("/contacto")
  }, t.cta))));
}
Object.assign(window, {
  Solutions
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/website/Solutions.jsx", error: String((e && e.message) || e) }); }

// ui_kits/website/copy.js
try { (() => {
window.LinkoCopy = {
  es: {
    nav: [{
      label: "Nosotros",
      href: "/nosotros"
    }, {
      label: "Soluciones",
      href: "/soluciones"
    }, {
      label: "Tecnología",
      href: "/tecnologia"
    }, {
      label: "Blog",
      href: "/blog"
    }],
    cta: "Contáctanos",
    heroTitle: "Soluciones tecnológicas simplificadas",
    heroSecondary: "Soluciones",
    positioning: "Conectando al mundo con innovación tecnológica",
    positioningBody: "Entendemos que la tecnología es una herramienta que te ayudará a crear mejores experiencias, operar de forma más eficiente o habilitar a tus colaboradores para hacer más.",
    stats: [["20+", "Años de experiencia"], ["100+", "Millones de clientes finales impactados"], ["500+", "Proyectos exitosos"], ["65+", "Arquitectos e ingenieros certificados"], ["20+", "Socios estratégicos"]],
    offerEyebrow: "Nuestra oferta",
    offerTitle: "Te ofrecemos el camino a las mejores experiencias digitales",
    solutions: [["Ciberseguridad", "Protege la información, las transacciones y la infraestructura crítica de tu negocio."], ["Integración", "Conecta aplicaciones, datos y dispositivos a través de APIs administradas."], ["Cloud & Data", "Construye la plataforma de datos que habilita decisiones inteligentes."], ["Transformación digital", "Rediseña procesos completos, no sólo las herramientas que los soportan."], ["Inteligencia artificial", "Automatiza el trabajo repetitivo y libera tiempo para lo que sí importa."]],
    casesTitle: "Casos de éxito",
    cases: [["Unidad de Auditoría - RPA", ["20% menos trabajo manual, errores humanos y revisiones.", "30% más productividad del equipo.", "2x más rápido el procesamiento de casos de auditoría."]], ["Banca - Data & Cloud", ["6 meses para crear un nuevo data lake.", "2x más rápida la implementación de ofertas personalizadas.", "+10% de incremento en créditos colocados."]], ["Grupo empresarial - Ciberseguridad", ["6 semanas para desplegar el nuevo sistema KSM.", "2 sistemas legados desmantelados sin impacto en la operación.", "10% de ahorro en costos operativos."]]],
    industriesTitle: "Transformamos industrias",
    industriesBody: "En Linko aprovechamos la relación cercana con nuestros clientes para entender su estrategia y acelerar su transformación digital.",
    industries: [["Servicios financieros", "Entrega ofertas altamente personalizadas basadas en inteligencia de datos y decisiones inteligentes."], ["Seguros", "Elimina tareas manuales y repetitivas para que tu equipo pase más tiempo frente al cliente."], ["Retail", "Libera tiempo para la innovación y el servicio con tiempos de respuesta más cortos."], ["Logística y transporte", "Optimiza recursos, procesos y rutas para dar la mejor experiencia a tus clientes."]],
    partnersTitle: "Soluciones tecnológicas simplificadas no es sólo un eslogan",
    partnersBody: "Nuestras alianzas con fabricantes de hardware y software de clase mundial nos mantienen a la vanguardia de la innovación tecnológica.",
    historyTitle: "Nuestra trayectoria",
    milestones: [["2002", "Nace Linko, desde entonces el objetivo era claro: ofrecer un servicio extraordinario y acelerar la transformación digital de nuestros clientes, ofreciendo experiencias digitales innovadoras y con tecnología de punta."], ["2004", "Se consolidan las primeras prácticas de integración empresarial y arquitectura orientada a servicios."], ["2012", "La práctica de ciberseguridad y protección de datos se vuelve una línea de negocio propia."], ["2019", "Automatización de procesos con RPA e inteligencia artificial para clientes de banca y seguros."], ["2024", "Cloud, datos e IA generativa se integran en una sola oferta de transformación."]],
    teamCaption: "Este es el equipo que hace de Linko una de las empresas más exitosas.",
    footerTagline: "Take the next step, simplified solutions.",
    footerSite: "Sitio",
    footerContact: "Contacto",
    footerBody: "Nuestro equipo de expertos está listo para asistirte en todo momento y llevar tu tecnología al siguiente nivel.",
    contactTitle: "Hablemos de tu próximo proyecto",
    contactBody: "Cuéntanos qué estás resolviendo y te conectamos con el equipo indicado.",
    formLabels: {
      name: "Nombre",
      email: "Correo corporativo",
      company: "Empresa",
      message: "¿En qué te ayudamos?"
    },
    formSubmit: "Enviar",
    formDone: "Gracias. Te contactaremos en menos de 24 horas.",
    legal: "© Linko 2026",
    privacy: "Aviso de privacidad",
    terms: "T&C"
  },
  en: {
    nav: [{
      label: "About us",
      href: "/nosotros"
    }, {
      label: "Solutions",
      href: "/soluciones"
    }, {
      label: "Technology",
      href: "/tecnologia"
    }, {
      label: "Blog",
      href: "/blog"
    }],
    cta: "Contact us",
    heroTitle: "Tech Solutions Made Simple",
    heroSecondary: "Solutions",
    positioning: "Linking the world with technological innovation",
    positioningBody: "We understand that technology is a tool that will help you create better experiences, operate more efficiently, or enable your collaborators to do more.",
    stats: [["20+", "Years of experience"], ["100+", "Millions of end clients impacted"], ["500+", "Successful projects"], ["65+", "Certified architects and engineers"], ["20+", "Strategic partners"]],
    offerEyebrow: "Our offer",
    offerTitle: "We offer the path to the best digital experiences",
    solutions: [["Cybersecurity", "Secure sensitive information, transactions and critical infrastructure."], ["Integration", "Connect applications, data and devices through managed APIs."], ["Cloud & Data", "Build the data platform that makes smart decisions possible."], ["Digital Transformation", "Redesign whole processes, not just the tools behind them."], ["Artificial Intelligence", "Automate repetitive work and free up time for what matters."]],
    casesTitle: "Success cases",
    cases: [["Audit Unit - RPA", ["20% decrease in manual labor, human errors, and revisions.", "30% increase in team productivity.", "2x faster processing for audit cases."]], ["Banking - Data & Cloud", ["6 months to create a new data lake.", "2x faster implementation of personalized offers.", "+10% increase in loans from the recommendation engine."]], ["Business Group - Cybersecurity", ["6 weeks to deploy the new KSM system.", "2 cybersecurity legacy systems decommissioned without impact.", "10% operating cost savings."]]],
    industriesTitle: "Transforming industries",
    industriesBody: "At Linko, we leverage our close and intimate relationships with our clients to understand their strategy and help them accelerate their digital transformation.",
    industries: [["Financial Services", "Deliver highly personalized offers to your clients based on data intelligence and smart decisions."], ["Insurance", "Eliminate manual and repetitive tasks from your team so they can spend more time in front of your clients."], ["Retail", "Free up more time for innovation and customer service with shorter turnaround times."], ["Logistics and transportation", "Optimize your resources, processes, and routes to provide the best experience for your customers."]],
    partnersTitle: "Tech solutions made simple is not just a slogan",
    partnersBody: "Our partnerships with world-class hardware and software manufacturers keeps us at the forefront of technological innovation.",
    historyTitle: "Our history",
    milestones: [["2002", "Linko is born. From day one the goal was clear: deliver extraordinary service and accelerate our clients' digital transformation."], ["2004", "The first enterprise integration and service-oriented architecture practices take shape."], ["2012", "Cybersecurity and data protection becomes a business line of its own."], ["2019", "Process automation with RPA and AI for banking and insurance clients."], ["2024", "Cloud, data and generative AI converge into a single transformation offer."]],
    teamCaption: "This is the team that makes Linko one of the most successful companies.",
    footerTagline: "Take the next step, simplified solutions.",
    footerSite: "Site",
    footerContact: "Contact",
    footerBody: "Our team of experts is ready to assist you at any time and take your technology to the next level.",
    contactTitle: "Let's talk about your next project",
    contactBody: "Tell us what you are solving and we'll connect you with the right team.",
    formLabels: {
      name: "Name",
      email: "Work email",
      company: "Company",
      message: "How can we help?"
    },
    formSubmit: "Send",
    formDone: "Thank you. We'll be in touch within 24 hours.",
    legal: "© Linko 2026",
    privacy: "Privacy policy",
    terms: "T&C"
  }
};
window.LinkoPartners = ["Thales", "UiPath", "Actico", "Salesforce", "MuleSoft", "TIBCO", "Google Cloud Platform", "Grafana"];
window.LinkoPartnerBlurbs = {
  "Thales": "Global technology company specialising in security and data protection: identity management, encryption and cybersecurity.",
  "UiPath": "Robotic process automation platform that automates repetitive tasks with software robots.",
  "Actico": "Business rule management, decision automation and compliance software.",
  "Salesforce": "CRM platform for sales, service, marketing and analytics.",
  "MuleSoft": "Integration platform connecting applications, data and devices through APIs.",
  "TIBCO": "Data integration and analytics platform for process optimisation.",
  "Google Cloud Platform": "Infrastructure, platform and application services on Google's cloud.",
  "Grafana": "Visualisation and dashboards over time-series metric data."
};
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/website/copy.js", error: String((e && e.message) || e) }); }

__ds_ns.RingMotif = __ds_scope.RingMotif;

__ds_ns.CaseCard = __ds_scope.CaseCard;

__ds_ns.IndustryCard = __ds_scope.IndustryCard;

__ds_ns.PartnerTile = __ds_scope.PartnerTile;

__ds_ns.SolutionCard = __ds_scope.SolutionCard;

__ds_ns.StatBlock = __ds_scope.StatBlock;

__ds_ns.TimelineCard = __ds_scope.TimelineCard;

__ds_ns.ArrowButton = __ds_scope.ArrowButton;

__ds_ns.ArrowLink = __ds_scope.ArrowLink;

__ds_ns.Button = __ds_scope.Button;

__ds_ns.Chip = __ds_scope.Chip;

__ds_ns.LangToggle = __ds_scope.LangToggle;

__ds_ns.Footer = __ds_scope.Footer;

__ds_ns.NavBar = __ds_scope.NavBar;

__ds_ns.SectionHeading = __ds_scope.SectionHeading;

})();
