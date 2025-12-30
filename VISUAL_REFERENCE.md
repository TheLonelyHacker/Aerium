# Responsive Breakpoint Visual Guide

## Device Size Reference

```
┌─────────────────────────────────────────────────────────────────────┐
│                         MOBILE (< 768px)                             │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                                                               │  │
│  │  [Logo] [Nav] [Status]                                        │  │
│  │  ────────────────────────────────                             │  │
│  │                                                               │  │
│  │  ┌─────────────────────────────────────────────────────────┐ │  │
│  │  │ Single Column Layout                                    │ │  │
│  │  │ - No overflow                                           │ │  │
│  │  │ - Large touch targets (44px)                            │ │  │
│  │  │ - Readable text (no zoom)                               │ │  │
│  │  │ - Responsive padding (12px)                             │ │  │
│  │  └─────────────────────────────────────────────────────────┘ │  │
│  │                                                               │  │
│  │  [Full Width Button]                                          │  │
│  │  [Full Width Button]                                          │  │
│  │                                                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘

                          TABLET (768px - 1024px)
    ┌───────────────────────────────────────────────────────────────┐
    │ [Logo]           [Nav Items]              [Status]            │
    │ ─────────────────────────────────────────────────────         │
    │                                                               │
    │  ┌────────────────────┐  ┌────────────────────┐              │
    │  │  Two Column Grid   │  │  Two Column Grid   │              │
    │  │  - Better spacing  │  │  - Better spacing  │              │
    │  │  - Balanced layout │  │  - Balanced layout │              │
    │  │                    │  │                    │              │
    │  └────────────────────┘  └────────────────────┘              │
    │                                                               │
    │  ┌──────────────────────────────────────────────────────┐   │
    │  │  Chart with better dimensions                       │   │
    │  └──────────────────────────────────────────────────────┘   │
    │                                                               │
    └───────────────────────────────────────────────────────────────┘

            DESKTOP (> 1025px)
    ┌─────────────────────────────────────────────────────────────────────┐
    │ [Logo]       [Nav Items Centered]              [Status - Full Text] │
    │ ───────────────────────────────────────────────────────────────     │
    │                                                                     │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
    │  │ Three Column     │  │ Three Column     │  │ Three Column     │ │
    │  │ - Hover effects  │  │ - Hover effects  │  │ - Hover effects  │ │
    │  │ - Full content   │  │ - Full content   │  │ - Full content   │ │
    │  │                  │  │                  │  │                  │ │
    │  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
    │                                                                     │
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ ┌──────────┐│
    │  │ Four Columns │  │ Four Columns │  │ Four Columns │ │ Four Col ││
    │  └──────────────┘  └──────────────┘  └──────────────┘ └──────────┘│
    │                                                                     │
    │  ┌──────────────────────────────────────────────────────────────┐ │
    │  │  Large Chart with Enhanced Hover Effects                    │ │
    │  │  - 400px height                                             │ │
    │  │  - Smooth animations                                        │ │
    └──────────────────────────────────────────────────────────────────┘
    └─────────────────────────────────────────────────────────────────────┘
```

---

## Navigation Changes by Device

### Mobile Layout
```
┌─────────────────────────────────────┐
│ [Logo] [≡] [•]                      │ ← Hamburger icon could go here
│ Home | Live | Settings | Analytics │
└─────────────────────────────────────┘
```

### Tablet Layout
```
┌──────────────────────────────────────────────────┐
│  [Logo]  Home | Live | Settings | Analytics  [•]│
│  ─────────────────────────────────────────────   │
└──────────────────────────────────────────────────┘
```

### Desktop Layout
```
┌─────────────────────────────────────────────────────────────────────┐
│  [Logo]     [Home] [Live] [Settings] [Analytics]    [• Active]     │
│  ────────────────────────────────────────────────────────────────   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Grid Transformation

### Mobile (1 Column)
```
┌──────────┐
│ Widget 1 │
└──────────┘
┌──────────┐
│ Widget 2 │
└──────────┘
┌──────────┐
│ Widget 3 │
└──────────┘
```

### Tablet (2 Columns)
```
┌──────────┐ ┌──────────┐
│ Widget 1 │ │ Widget 2 │
└──────────┘ └──────────┘
┌──────────┐
│ Widget 3 │
└──────────┘
```

### Desktop (3-4 Columns)
```
┌──────────┐ ┌──────────┐ ┌──────────┐
│ Widget 1 │ │ Widget 2 │ │ Widget 3 │
└──────────┘ └──────────┘ └──────────┘
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Widget 4 │ │ Widget 5 │ │ Widget 6 │ │ Widget 7 │
└──────────┘ └──────────┘ └──────────┘ └──────────┘
```

---

## Touch Target Sizing

### Too Small (Avoid)
```
[B] ← 24×24px button (too small to touch reliably)
```

### Perfect (Target)
```
┌────────────────┐
│                │
│    [Button]    │ ← 44×44px minimum
│                │
└────────────────┘
```

### With Spacing
```
┌────────────────┐
│                │
│    [Button]    │
│                │  8px spacing
├────────────────┤
│                │
│    [Button]    │
│                │
└────────────────┘
```

---

## Typography Scaling

### Mobile
```
┌────────────────┐
│ Morpheus       │ ← 1.8rem (h1)
│                │
│ Surveillance   │ ← 0.95rem (body)
│ of CO₂         │
│                │
│ Widget Title   │ ← 1.3rem (h2)
│ Label          │ ← 0.8rem (label)
│ Hint text      │ ← 0.75rem (hint)
└────────────────┘
```

### Desktop
```
┌──────────────────────────┐
│ Morpheus                 │ ← 2.2rem (h1)
│                          │
│ Surveillance of CO₂      │ ← 1rem (body)
│                          │
│ Widget Title             │ ← 1.5rem (h2)
│ Label                    │ ← 0.9rem (label)
│ Hint text                │ ← 0.8rem (hint)
└──────────────────────────┘
```

---

## Padding & Spacing Progression

```
Mobile                  Tablet                  Desktop
(12px)                 (16px)                  (20px)

┌──────┐              ┌───────┐               ┌────────┐
│padding│              │padding│               │padding │
├──────┤              ├───────┤               ├────────┤
│      │              │       │               │        │
│ Card │              │ Card  │               │  Card  │
│      │              │       │               │        │
├──────┤              ├───────┤               ├────────┤
│padding│              │padding│               │padding │
└──────┘              └───────┘               └────────┘
Gap: 8px             Gap: 12px               Gap: 16px
```

---

## Button Layout Transformation

### Mobile (Stacked)
```
[Full Width Button 1]
[Full Width Button 2]
[Full Width Button 3]
```

### Tablet (Wrapped)
```
[Button 1] [Button 2]
[Button 3]
```

### Desktop (Row)
```
[Button 1] [Button 2] [Button 3]
```

---

## Chart Sizing

### Mobile
```
┌─────────────────┐
│                 │
│   Chart         │  Height: 220px
│   (Responsive)  │  Width: 100%
│                 │
└─────────────────┘
```

### Tablet
```
┌──────────────────────────────┐
│                              │
│      Chart                   │  Height: 280px
│      (Responsive)            │  Width: 100%
│                              │
└──────────────────────────────┘
```

### Desktop
```
┌──────────────────────────────────────────────┐
│                                              │
│             Chart                            │  Height: 400px
│             (Responsive with hover)          │  Width: 100%
│                                              │
│                                              │
└──────────────────────────────────────────────┘
```

---

## Focus State Visualization

### Normal State
```
[Button Text]
```

### Focused State (Keyboard)
```
╔════════════════╗
║ [Button Text]  ║  ← 2px green outline
╚════════════════╝    2px offset
```

### Focused Button
```
╭─────────────────────╮
│ ┌─────────────────┐ │
│ │ [Button Text]   │ │  ← Multiple focus rings
│ └─────────────────┘ │
╰─────────────────────╯
```

---

## Responsive Image Example

### Mobile
```
┌──────────┐
│          │
│ Image    │  Width: 100%
│          │  Height: Auto
│          │  Max-width: 100%
└──────────┘
```

### Desktop
```
┌──────────────────────────────┐
│                              │
│         Image                │  Width: 100%
│                              │  Max-width: 600px
│                              │  Height: Auto
│                              │
└──────────────────────────────┘
```

---

## Color Palette Application

```
Background: #0b0d12 (Dark blue-black)
┌─────────────────────────────────────────┐
│  Text: #e5e7eb (Light gray)             │
│  Muted: #9ca3af (Medium gray)           │
│                                         │
│  Card: #141826                          │
│  ┌─────────────────────────────────┐   │
│  │ Good: #4ade80 (Green)           │   │
│  │ Medium: #facc15 (Yellow)        │   │
│  │ Bad: #f87171 (Red)              │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

## Animation Timing Reference

```
Instant:     0ms - Button press feedback
Quick:    100ms - Hover effects
Standard: 200ms - Color/background changes
Smooth:   300ms - Property animations
Slow:     400ms - State transitions
  |
  ├─→ Page load: 800ms (heroFade)
  ├─→ Chart update: 450ms
  └─→ Transitions: 350ms (cubic-bezier)
```

---

## CSS Media Query Reference

```
                    Mobile      Tablet      Desktop
                    |-----------|-----------|------------|
Screen Width        < 768px     768-1024    > 1024px
                    |___________|___________|___________|

Padding             12px        16px        20px
Font Size (h1)      1.8rem      2rem        2.2rem
Font Size (body)    0.95rem     0.95rem     1rem
Grid Columns        1           2           3-4
Touch Target        44×44px     48×48px     (hover states)
Container Max       100%        100%        1100px
```

---

## Mobile-First Development Order

```
1. Design mobile layout (base styles)
   ↓
2. Add @media (min-width: 769px) for tablet
   ↓
3. Add @media (min-width: 1025px) for desktop
   ↓
4. Test on actual devices
   ↓
5. Add accessibility features
   ↓
6. Optimize for performance
   ↓
7. Document for future devs
```

This ensures a solid foundation that enhances for larger screens.
