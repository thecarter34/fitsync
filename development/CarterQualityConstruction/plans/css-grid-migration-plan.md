# CSS Grid Migration Plan: Mobile/Desktop Viewpoint Isolation

## Executive Summary

The current `index.html` has **significant CSS conflicts** between mobile (`max-width: 768px`) and desktop styles. The root cause is that both viewports share the same CSS selectors with overlapping properties, causing edits to one to break the other. This plan migrates the layout to **CSS Grid with Named Areas**, creating two isolated layout maps that cannot interfere with each other.

---

## Current Architecture Analysis

### Major Page Sections Identified

| Section        | Current Class                     | Current Layout Method                  | Issues                                                             |
| -------------- | --------------------------------- | -------------------------------------- | ------------------------------------------------------------------ |
| Navigation     | `nav` / `.nav-container`          | Flexbox with `!important` overrides    | Mobile uses `!important` on 50+ properties                         |
| Hero           | `.hero`                           | Absolute positioning + flexbox overlay | Video `position: fixed` conflicts with mobile `position: absolute` |
| Vision/Reality | `.making-dreams`                  | Block with text-align                  | Minimal issues                                                     |
| Services       | `.services` / `.services-grid`    | CSS Grid (already)                     | Good foundation, needs isolation                                   |
| About          | `.about` / `.about-container`     | CSS Grid (already)                     | Good foundation, needs isolation                                   |
| Testimonials   | `.testimonials`                   | Absolute-positioned slider             | Fixed height causes issues                                         |
| Contact        | `.contact` / `.contact-container` | CSS Grid (already)                     | Good foundation, needs isolation                                   |
| Footer         | `footer` / `.footer-content`      | CSS Grid (auto-fit)                    | Works but needs refinement                                         |

### Root Causes of Mobile/Desktop Conflicts

1. **Duplicate Selector Definitions**: The same selectors (`.hero`, `.hero-overlay`, `.hero-video-background`) are defined multiple times with conflicting values across media queries
2. **`!important` Overuse**: 50+ `!important` declarations in mobile media query override desktop styles unpredictably
3. **Mixed Positioning Strategies**: `position: fixed` vs `position: absolute` for same elements across breakpoints
4. **Inline `height: 100vh` Overrides**: Desktop styles override mobile `height: 85vh !important` with `height: 100vh`
5. **No Structural Separation**: Mobile and desktop layouts share the same grid-area definitions

---

## Proposed CSS Grid Architecture

### Grid Area Naming Convention

```
Grid Area Names (BEM-inspired):
- "nav"         → Navigation bar
- "hero"        → Hero section with video
- "vision"      → "What We Do" section
- "services"    → Services grid section
- "about"       → About section
- "testimonials"→ Testimonials slider
- "contact"     → Contact form section
- "footer"      → Footer section
```

### Page-Level Grid Container

Create a **single page-level grid container** that wraps all major sections. This container will have two distinct `grid-template-areas` definitions:

```css
/* Base: Mobile Layout (single column stack) */
.page-grid {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-areas:
    "nav"
    "hero"
    "vision"
    "services"
    "about"
    "testimonials"
    "contact"
    "footer";
}

/* Desktop Layout (1024px+ breakpoint) */
@media (min-width: 1024px) {
  .page-grid {
    grid-template-columns: 1fr min(1200px, 90vw) 1fr;
    grid-template-areas:
      ".    nav         ."
      ".    hero        ."
      ".    vision      ."
      ".    services    ."
      ".    about       ."
      ".    testimonials."
      ".    contact     ."
      ".    footer      .";
  }
}
```

### Section-Level Grid Areas

Each major section gets its own internal grid with named areas for its children:

#### Hero Section Grid

```css
.hero-grid {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-areas:
    "video-bg"
    "overlay";
}

.hero-grid > .hero-video-background {
  grid-area: video-bg;
}
.hero-grid > .hero-overlay {
  grid-area: overlay;
}
```

#### Navigation Grid

```css
.nav-grid {
  display: grid;
  grid-template-columns: auto 1fr;
  grid-template-areas: "logo links";
  align-items: center;
}

@media (min-width: 1024px) {
  .nav-grid {
    grid-template-columns: auto 1fr auto;
    grid-template-areas: "logo links cta";
  }
}
```

---

## Step-by-Step Implementation Guide

### Phase 1: Preparation (Structural HTML Changes)

**Step 1.1: Add Page Grid Wrapper**

Wrap all page content in a `.page-grid` container:

```html
<body>
  <a href="#main-content" class="skip-link">Skip to main content</a>

  <div class="page-grid">
    <!-- All sections get grid-area assignment -->
    <nav class="nav-grid" style="grid-area: nav;">...</nav>
    <section class="hero-grid" style="grid-area: hero;">...</section>
    <section class="vision-section" style="grid-area: vision;">...</section>
    <section class="services-section" style="grid-area: services;">...</section>
    <section class="about-section" style="grid-area: about;">...</section>
    <section class="testimonials-section" style="grid-area: testimonials;">
      ...
    </section>
    <section class="contact-section" style="grid-area: contact;">...</section>
    <footer class="footer-section" style="grid-area: footer;">...</footer>
  </div>
</body>
```

**Step 1.2: Add Hero Internal Grid Structure**

```html
<section class="hero hero-grid" id="home" aria-label="Hero banner">
  <div class="hero-video-background" style="grid-area: hero-video;">
    <video>...</video>
  </div>
  <div class="hero-overlay" style="grid-area: hero-overlay;">
    <!-- overlay content -->
  </div>
</section>
```

**Step 1.3: Add Nav Internal Grid Structure**

```html
<nav class="nav-grid" id="navbar" role="navigation">
  <a href="#home" class="nav-logo" style="grid-area: nav-logo;">...</a>
  <ul class="nav-links" style="grid-area: nav-links;">
    ...
  </ul>
</nav>
```

---

### Phase 2: CSS Grid Foundation

**Step 2.1: Create New CSS File**

Create `grid-layout.css` with the following structure:

```css
/* ==========================================
   PAGE-LEVEL GRID LAYOUT
   Carter Quality Construction
   ========================================== */

/* --- Mobile Layout (default) --- */
.page-grid {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-areas:
    "nav"
    "hero"
    "vision"
    "services"
    "about"
    "testimonials"
    "contact"
    "footer";
  min-height: 100vh;
}

/* --- Desktop Layout (1024px+) --- */
@media (min-width: 1024px) {
  .page-grid {
    grid-template-columns: 1fr min(1200px, 90vw) 1fr;
    grid-template-areas:
      ".    nav           ."
      ".    hero          ."
      ".    vision        ."
      ".    services      ."
      ".    about         ."
      ".    testimonials  ."
      ".    contact       ."
      ".    footer        .";
  }
}

/* --- Wide Desktop (1440px+) --- */
@media (min-width: 1440px) {
  .page-grid {
    grid-template-columns: 1fr 1400px 1fr;
  }
}
```

**Step 2.2: Assign Grid Areas to Sections**

```css
/* Grid area assignments */
.nav-grid {
  grid-area: nav;
}
.hero-grid {
  grid-area: hero;
}
.vision-section {
  grid-area: vision;
}
.services-section {
  grid-area: services;
}
.about-section {
  grid-area: about;
}
.testimonials-section {
  grid-area: testimonials;
}
.contact-section {
  grid-area: contact;
}
.footer-section {
  grid-area: footer;
}
```

---

### Phase 3: Section-Specific Grid Layouts

**Step 3.1: Hero Section Grid**

```css
/* Hero internal grid - Mobile */
.hero-grid {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: 100vh;
  grid-template-areas:
    "hero-video"
    "hero-overlay";
  position: relative;
  overflow: hidden;
}

.hero-grid > .hero-video-background {
  grid-area: hero-video;
  position: absolute;
  inset: 0;
  z-index: 0;
}

.hero-grid > .hero-overlay {
  grid-area: hero-overlay;
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-columns: 1fr;
  grid-template-areas:
    "hero-logo"
    "hero-content"
    "hero-cta"
    "hero-rating";
  place-items: center;
  padding: 2rem 1rem;
}

/* Hero overlay children */
.hero-logo {
  grid-area: hero-logo;
}
.hero-text-content {
  grid-area: hero-content;
}
.hero-cta-group {
  grid-area: hero-cta;
}
.hero-rating-card {
  grid-area: hero-rating;
}
```

**Step 3.2: Navigation Grid**

```css
/* Nav internal grid - Mobile */
.nav-grid {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: auto auto;
  grid-template-areas:
    "nav-logo"
    "nav-links";
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 300;
  padding: 0.5rem;
}

.nav-grid > .nav-logo {
  grid-area: nav-logo;
  justify-self: center;
}

.nav-grid > .nav-links {
  grid-area: nav-links;
  display: flex;
  flex-direction: row;
  justify-content: space-evenly;
  overflow-x: auto;
}

/* Nav internal grid - Desktop (1024px+) */
@media (min-width: 1024px) {
  .nav-grid {
    grid-template-columns: auto 1fr;
    grid-template-rows: 1fr;
    grid-template-areas: "nav-logo nav-links";
    padding: 0.2rem 0.5rem;
  }

  .nav-grid > .nav-logo {
    justify-self: start;
  }

  .nav-grid > .nav-links {
    justify-content: flex-end;
    gap: 2rem;
  }
}
```

**Step 3.3: Services Grid (Already Grid - Refine)**

```css
/* Services grid - Mobile */
.services-grid {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-areas:
    "service-1"
    "service-2"
    "service-3"
    "service-4";
  gap: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

/* Services grid - Tablet (640px+) */
@media (min-width: 640px) {
  .services-grid {
    grid-template-columns: repeat(2, 1fr);
    grid-template-areas:
      "service-1 service-2"
      "service-3 service-4";
  }
}

/* Services grid - Desktop (1024px+) */
@media (min-width: 1024px) {
  .services-grid {
    grid-template-columns: repeat(3, 1fr);
    grid-template-areas:
      "service-1 service-2 service-3"
      "service-4 .           .";
  }
}

/* Services grid - Wide Desktop (1280px+) */
@media (min-width: 1280px) {
  .services-grid {
    grid-template-columns: repeat(4, 1fr);
    grid-template-areas: "service-1 service-2 service-3 service-4";
  }
}

/* Assign areas to cards */
.service-card:nth-child(1) {
  grid-area: service-1;
}
.service-card:nth-child(2) {
  grid-area: service-2;
}
.service-card:nth-child(3) {
  grid-area: service-3;
}
.service-card:nth-child(4) {
  grid-area: service-4;
}
```

**Step 3.4: About Section Grid**

```css
/* About internal grid - Mobile */
.about-section {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-areas:
    "about-content"
    "about-image";
  gap: 3rem;
  max-width: 1200px;
  margin: 0 auto;
  padding: 4rem 1rem;
}

.about-content {
  grid-area: about-content;
}
.about-image {
  grid-area: about-image;
}

/* About internal grid - Desktop (1024px+) */
@media (min-width: 1024px) {
  .about-section {
    grid-template-columns: 1fr 1fr;
    grid-template-areas: "about-content about-image";
    gap: 4rem;
    padding: 6rem 2rem;
  }
}
```

**Step 3.5: Contact Section Grid**

```css
/* Contact internal grid - Mobile */
.contact-section {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-areas:
    "contact-header"
    "contact-info"
    "contact-form";
  gap: 3rem;
  max-width: 1200px;
  margin: 0 auto;
  padding: 4rem 1rem;
}

.contact-header {
  grid-area: contact-header;
}
.contact-info {
  grid-area: contact-info;
}
.contact-form {
  grid-area: contact-form;
}

/* Contact internal grid - Desktop (1024px+) */
@media (min-width: 1024px) {
  .contact-section {
    grid-template-columns: 1fr 1fr;
    grid-template-areas:
      "contact-header contact-header"
      "contact-info   contact-form";
    gap: 4rem;
    padding: 6rem 2rem;
  }
}
```

**Step 3.6: Footer Grid**

```css
/* Footer internal grid - Mobile */
.footer-section {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-areas:
    "footer-brand"
    "footer-links"
    "footer-services"
    "footer-contact"
    "footer-social"
    "footer-bottom";
  gap: 2rem;
  padding: 3rem 1rem 1.5rem;
}

/* Footer internal grid - Desktop (768px+) */
@media (min-width: 768px) {
  .footer-section {
    grid-template-columns: repeat(4, 1fr);
    grid-template-areas:
      "footer-brand    footer-links  footer-services footer-contact"
      "footer-social   footer-social footer-social   footer-social"
      "footer-bottom   footer-bottom footer-bottom   footer-bottom";
    max-width: 1200px;
    margin: 0 auto;
  }
}
```

---

### Phase 4: Cleanup - Remove Legacy CSS

**Step 4.1: Remove Conflicting Mobile Overrides**

Delete or refactor these problematic patterns from `index.html` `<style>` block:

| Lines to Remove/Refactor                             | Issue                                                        | Replacement                                     |
| ---------------------------------------------------- | ------------------------------------------------------------ | ----------------------------------------------- |
| Lines 324-847 (mobile media query with `!important`) | 50+ `!important` overrides                                   | Replace with `.nav-grid` mobile grid definition |
| Lines 962-987 (hero height overrides)                | Conflicting `height: 100vh` definitions                      | Use `grid-template-rows` in `.hero-grid`        |
| Lines 1154-1245 (duplicate hero definitions)         | Duplicate `.hero`, `.hero-video-background`, `.hero-overlay` | Consolidate into `.hero-grid`                   |
| Lines 2640-2728 (responsive overrides)               | Grid template column resets                                  | Already handled by section grids                |
| Lines 2664-2707 (mobile hero video)                  | Duplicate video positioning                                  | Use `grid-area: hero-video`                     |

**Step 4.2: Remove Legacy Positioning**

Remove these patterns:

```css
/* REMOVE: Float-based layouts (none found, but verify) */
/* REMOVE: Absolute positioning for layout (keep for decorative elements) */
/* REMOVE: Inline styles that override grid */
```

**Step 4.3: Clean Up External CSS**

In `enhanced-hero-styles.css`:

| Lines to Refactor                       | Issue                              | Replacement                        |
| --------------------------------------- | ---------------------------------- | ---------------------------------- |
| Lines 280-306 (mobile nav responsive)   | Conflicts with inline `!important` | Use `.nav-grid` desktop definition |
| Lines 474-584 (mobile hero video)       | Duplicate overlay definitions      | Consolidate into `.hero-grid`      |
| Lines 581-615 (mobile hero adjustments) | Overlaps with inline styles        | Use grid-area definitions          |

---

### Phase 5: Structural Isolation Verification

**Step 5.1: Verify Mobile Independence**

Test that mobile layout works without any desktop styles:

```css
/* Test: Mobile-only stylesheet should produce complete layout */
.page-grid {
  /* Single column stack - no desktop dependencies */
}
```

**Step 5.2: Verify Desktop Independence**

Test that desktop layout doesn't inherit mobile positioning:

```css
/* Test: Desktop media query should redefine all layout properties */
@media (min-width: 1024px) {
  .page-grid {
    /* Multi-column grid - no mobile property inheritance */
  }
}
```

**Step 5.3: Cross-Breakpoint Testing**

| Test Case                | Expected Result                |
| ------------------------ | ------------------------------ |
| Edit mobile nav padding  | Desktop nav unchanged          |
| Edit desktop hero height | Mobile hero unchanged          |
| Edit mobile services gap | Desktop services gap unchanged |
| Edit desktop about grid  | Mobile about stack unchanged   |

---

## Mermaid Architecture Diagram

```mermaid
graph TD
    subgraph Page Grid Container
        A[nav-grid] --> B[hero-grid]
        B --> C[vision-section]
        C --> D[services-section]
        D --> E[about-section]
        E --> F[testimonials-section]
        F --> G[contact-section]
        G --> H[footer-section]
    end

    subgraph Mobile Layout < 1024px
        A1[single column stack]
    end

    subgraph Desktop Layout >= 1024px
        A2[centered column with side gutters]
    end

    subgraph Hero Internal Grid
        B1[hero-video - absolute background]
        B2[hero-overlay - flexbox centering]
    end

    subgraph Nav Internal Grid
        C1[Mobile: 2 rows - logo + links]
        C2[Desktop: 1 row - logo + links]
    end

    B --> B1
    B --> B2
    A --> C1
    A --> C2
```

---

## Implementation Order

1. **Create `grid-layout.css`** - New file with all grid definitions
2. **Add HTML wrappers** - Add `.page-grid`, `.hero-grid`, `.nav-grid`, etc.
3. **Link new CSS** - Add `<link rel="stylesheet" href="grid-layout.css">` to `<head>`
4. **Test mobile layout** - Verify single-column stack works
5. **Test desktop layout** - Verify multi-column grid works
6. **Remove legacy CSS** - Delete conflicting mobile overrides from `index.html`
7. **Clean up `enhanced-hero-styles.css`** - Remove duplicate definitions
8. **Final testing** - Cross-browser, cross-device verification

---

## Risk Mitigation

| Risk                         | Mitigation                                                                              |
| ---------------------------- | --------------------------------------------------------------------------------------- |
| Breaking existing animations | Grid only affects layout; animations remain on child elements                           |
| JavaScript selector changes  | Add new classes alongside existing ones; remove old classes after testing               |
| Video positioning conflicts  | Use `grid-area` for placement; keep `position: absolute` for video within its grid cell |
| Performance regression       | Grid is GPU-accelerated; fewer `!important` overrides improve rendering                 |

---

## Files to Modify

| File                       | Changes                                                          |
| -------------------------- | ---------------------------------------------------------------- |
| `index.html`               | Add grid wrapper classes, remove legacy CSS from `<style>` block |
| `enhanced-hero-styles.css` | Remove duplicate mobile overrides, consolidate hero styles       |
| `grid-layout.css`          | **NEW** - Contains all grid definitions                          |
