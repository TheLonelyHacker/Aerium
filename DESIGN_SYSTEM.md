# Design System - Morpheus CO₂ Monitoring

## Color Palette

### Primary Colors
```css
--bg:     #0b0d12  /* Deep blue-black background */
--card:   #141826  /* Slightly lighter for cards */
--text:   #e5e7eb  /* Light gray text */
--muted:  #9ca3af  /* Medium gray for secondary text */
```

### Status Colors
```css
--good:   #4ade80  /* Green - Air is healthy */
--medium: #facc15  /* Yellow - Air is moderate */
--bad:    #f87171  /* Red - Air is poor */
```

### Color Usage Guide
| Element | Color | Usage |
|---------|-------|-------|
| Backgrounds | `--bg` | Page, cards background |
| Cards | `--card` | Card container background |
| Primary Text | `--text` | Main content, headings |
| Secondary Text | `--muted` | Labels, hints, inactive |
| Success/Good | `--good` | Good air quality, buttons |
| Warning/Medium | `--medium` | Medium air quality |
| Error/Bad | `--bad` | Poor air quality, warnings |

---

## Typography Scale

### Heading Hierarchy
```css
h1  { font-size: 2.2rem; font-weight: 700; }  /* Hero titles */
h2  { font-size: 1.5rem; font-weight: 600; }  /* Section titles */
h3  { font-size: 1.2rem; font-weight: 600; }  /* Subsection titles */
h4  { font-size: 1.1rem; font-weight: 600; }  /* Component titles */
```

### Text Styles
```css
body  { font-size: 0.95rem; line-height: 1.6; }
label { font-size: 0.9rem; font-weight: 500; }
hint  { font-size: 0.8rem; color: var(--muted); }
```

### Font Stack
```css
font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
```

---

## Spacing Scale

### Standard Spacing Units (in pixels)
```
4px   - Extra small gaps
8px   - Small components
12px  - Medium spacing
16px  - Default padding
20px  - Large padding
24px  - Extra large spacing
28px  - Section spacing
32px  - Major section spacing
```

### Common Spacing Patterns
```css
padding:  8px 16px        /* Buttons, links */
padding:  16px            /* Cards interior */
padding:  20-25px         /* Card section padding */
margin:   12px 0          /* Vertical margins */
gap:      12-16px         /* Grid gaps */
border-radius: 8-14px     /* Consistent radius */
```

---

## Component Specifications

### Buttons
```css
/* States */
Default:  background: var(--good), padding: 10px 18px
Hover:    background lighter, transform: translateY(-2px)
Focus:    outline: 2px solid var(--good), outline-offset: 2px
Active:   transform: scale(0.96)

/* Sizes */
Small:  padding: 6px 12px
Normal: padding: 10px 18px
Large:  padding: 12px 24px

/* Touch */
min-width: 44px; min-height: 44px;
```

### Cards
```css
background:  var(--card)
padding:     25px (desktop) → 16px (mobile)
border:      1px solid rgba(255, 255, 255, 0.05)
border-radius: 14px
box-shadow:  0 10px 30px rgba(0, 0, 0, 0.3)
margin-bottom: 28px
```

### Links
```css
padding:  8px 16px
border-radius: 8px
color:    var(--muted) or var(--good)
transition: all 0.2s ease

Hover: background: rgba(255, 255, 255, 0.05)
Focus: outline: 2px solid var(--good)
```

### Form Inputs
```css
/* Sliders */
height: 6px
thumb: 20px diameter
background: rgba(255, 255, 255, 0.15)
accent: var(--good)

/* Toggles */
width: 56px; height: 30px
border-radius: 999px
checked color: var(--good)

/* Inputs */
padding: 8px 12px
border-radius: 8px
border: 1px solid rgba(255, 255, 255, 0.08)
background: rgba(255, 255, 255, 0.03)
```

---

## Shadows & Depth

### Shadow Elevation Levels
```css
/* Subtle - Cards, small elements */
box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);

/* Medium - Floating elements */
box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);

/* Strong - Modals, dropdowns */
box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5);

/* Inset - Depth within cards */
box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
```

---

## Borders & Strokes

### Border Styles
```css
/* Light borders */
border: 1px solid rgba(255, 255, 255, 0.05);

/* Medium borders */
border: 1px solid rgba(255, 255, 255, 0.08);

/* Accent borders */
border: 1px solid rgba(74, 222, 128, 0.3);  /* Good state */
border: 1px solid rgba(250, 204, 21, 0.3);  /* Medium state */
border: 1px solid rgba(248, 113, 113, 0.3); /* Bad state */

/* Dashed borders */
border: 1px dashed rgba(255, 255, 255, 0.12);
```

### Border Radius
```css
border-radius: 6px   /* Small elements */
border-radius: 8px   /* Buttons, inputs */
border-radius: 12px  /* Medium components */
border-radius: 14px  /* Cards, sections */
border-radius: 18px  /* Large sections */
border-radius: 999px /* Pills, rounded buttons */
```

---

## Animations & Transitions

### Standard Timing
```css
/* Quick feedback */
transition: 0.15s ease;  /* Button presses */

/* Smooth transitions */
transition: 0.2s ease;   /* Color/background changes */
transition: 0.3s ease;   /* Property changes */

/* Longer animations */
transition: 0.4s ease;   /* Important state changes */
transition: 0.5s ease;   /* Page transitions */
```

### Easing Functions
```css
/* Linear */
transition-timing-function: linear;

/* Ease (default) */
transition-timing-function: ease;

/* Ease-out (recommended for UI) */
transition-timing-function: cubic-bezier(0.22, 1, 0.36, 1);

/* Ease-in */
transition-timing-function: ease-in;
```

### Common Animations
```css
/* Pulse - Status updates */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* Fade - Entrance/exit */
@keyframes fade {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Scale - Feedback */
@keyframes scale {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}
```

---

## Responsive Breakpoints

### Device Categories
```css
Mobile:   max-width: 768px
Tablet:   768px to 1024px
Desktop:  1025px and above
```

### Key Breakpoints
```css
320px   /* Small phones */
480px   /* Regular phones */
768px   /* Tablets portrait */
1024px  /* Tablets landscape */
1280px  /* Small desktops */
1920px  /* Large desktops */
```

---

## Accessibility Standards

### WCAG Compliance
- **Color Contrast**: Minimum AA standard (4.5:1 for text)
- **Focus Indicators**: Visible on all interactive elements
- **Touch Targets**: Minimum 44×44px for mobile
- **Font Size**: Readable without zooming

### Focus State Specification
```css
outline: 2px solid var(--good);
outline-offset: 2px;
```

### Motion Preferences
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Dark/Light Mode

### Light Mode Variables (Optional)
```css
@media (prefers-color-scheme: light) {
  --bg: #f5f5f5;
  --card: #ffffff;
  --text: #1a1a1a;
  --muted: #666666;
}
```

---

## Best Practices

### Do's ✓
- Use CSS variables for consistent theming
- Maintain 1.6 line-height for readability
- Use semantic HTML elements
- Provide focus indicators on all interactive elements
- Test on actual mobile devices
- Use touch-friendly spacing

### Don'ts ✗
- Don't use exact pixel sizes for responsive design
- Don't remove focus outlines
- Don't use color alone to convey information
- Don't make touch targets smaller than 44×44px
- Don't use animations that flash more than 3 times per second
- Don't auto-play videos or sounds

---

## Implementation Examples

### Button Component
```html
<button class="link primary">
  📊 Voir le live
</button>

<style>
.link {
  display: inline-block;
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.link:focus { outline: 2px solid var(--good); outline-offset: 2px; }
.link.primary { background: var(--good); color: var(--bg); }
</style>
```

### Card Component
```html
<section class="card">
  <h2>Title</h2>
  <p>Content...</p>
</section>

<style>
.card {
  background: var(--card);
  padding: 25px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  margin-bottom: 28px;
}
</style>
```

---

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Material Design](https://material.io/design)
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines)
