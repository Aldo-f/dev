# Improve Dark Theme Plan

## Goal
The dark theme looks untidy with inconsistent colors, poor contrast, and misaligned components across the footer and overall site.

## Current context / assumptions
- Site uses CSS variables for theming with light/dark token sets
- Footer currently has basic styling but lacks proper dark mode contrast
- AGENTS.md requires minimal changes to templates only, runtime dirs regenerated via Ansible
- HTML structure follows homepage component patterns (`#footer`, `.information-widget-*`, `.bookmark-*`, `.resource-usage`)
- Must maintain neon-brutalist aesthetic: sharp borders, bold shadows, high contrast
- No Node/JS build; only CSS edits in `/home/aldo/dev/06-apps-neo-brutalist-home/config/`
- Existing custom.css already has dark mode variables but lacks specific rule sets
- Footer switcher button exists but dark mode lacks visual polish

## Architecture / proposed approach
Improve dark theme by:
- Extending existing `:root` and `.dark :root` variable sets to add more refined neutrals, accent variants, and subtle texture
- Adding comprehensive dark-mode-specific rules for footer, cards, widgets, and interactive elements
- Ensuring proper contrast ratios (WCAG AA) for text and UI elements
- Maintaining brand consistency: neon-brutalist style (border, shadow, translate hover)
- Targeting problematic areas: footer background/text, progress bar track fill, status badges, focus states

## Step-by-step tasks

### Task 1: Add refined dark color palette variables
- File: `/home/aldo/dev/06-apps-neo-brutalist-home/config/custom.css`
- Before line 21 (after `/* Design Tokens - PINO inspired colors */`)
- Add: 
  ```css
  /* Dark mode enhanced palette */
  .dark :root {
    /* Refined background and surface tokens */
    --nb-paper-dark: #16161d;        /* Slightly lighter than current paper */
    --nb-ink-dark: #e1e1e8;          /* Brighter ink for better readability */
    --nb-border-dark: #3a3a45;       /* Distinct border */
    --nb-shadow-dark: 6px 6px 0 #1a1a30;
    /* Enhanced accent variants */
    --nb-lime-dark: #b3ff33;        /* Brighter lime for dark mode */
    --nb-neon-dark: #ff6633;        /* Softer neon for reduced eye strain */
    --nb-blue-dark: #6699ff;
    --nb-purple-dark: #b366ff;
    /* Status colors for dark mode */
    --status-success: #22c55e;
    --status-warning: #fbbf24;
    --status-error: #ef4444;
    --status-info: #3b82f6;
  }
  ```
- Verification: `grep -n "nb-lime-dark" /home/aldo/dev/06-apps-neo-brutalist-home/config/custom.css`

### Task 2: Override dark theme components base styles
- File: `/home/aldo/dev/06-apps-neo-brutalist-home/config/custom.css`
- Before line 33 (before `/* ===== PAGE BACKGROUND ===== */`)
- Add:
  ```css
  /* Dark theme base component overrides */
  .dark body,
  [data-theme="dark"] body {
    background: var(--nb-paper-dark) !important;
    color: var(--nb-ink-dark) !important;
  }
  
  .dark .service-group-name,
  [data-theme="dark"] .service-group-name {
    background: var(--nb-lime-dark) !important;
    color: var(--nb-ink-dark) !important;
    border-color: var(--nb-border-dark) !important;
    box-shadow: 4px 4px 0 var(--nb-neon-dark) !important;
  }
  
  .dark li.service,
  [data-theme="dark"] li.service {
    background: var(--nb-paper-dark) !important;
    border-color: var(--nb-border-dark) !important;
    box-shadow: var(--nb-shadow-dark) !important;
  }
  
  .dark li.service:hover,
  [data-theme="dark"] li.service:hover {
    box-shadow: 10px 10px 0 var(--nb-purple-dark) !important;
  }
  ```
- Verification: Search for `.dark li.service` in file

### Task 3: Style information widgets for dark mode
- File: `/home/aldo/dev/06-apps-neo-brutalist-home/config/custom.css`
- Before line 167 (before `/* ===== INFORMATION WIDGETS ===== */`)
- Add:
  ```css
  /* Information widgets dark mode */
  .dark .information-widget-resource,
  [data-theme="dark"] .information-widget-resource {
    background: var(--nb-paper-dark) !important;
    border-color: var(--nb-border-dark) !important;
    box-shadow: 4px 4px 0 var(--nb-lime-dark) !important;
    color: var(--nb-ink-dark) !important;
  }
  
  .dark .information-widget-label,
  [data-theme="dark"] .information-widget-label {
    color: var(--nb-ink-dark) !important;
    opacity: 0.8 !important;
  }
  
  .dark .resource-usage,
  [data-theme="dark"] .resource-usage {
    background: #2a2a40 !important;      /* Darker track */
    border-color: var(--nb-border-dark) !important;
  }
  
  .dark .resource-usage > div,
  [data-theme="dark"] .resource-usage > div {
    background: var(--nb-lime-dark) !important;
  }
  ```
- Verification: Check `.dark .information-widget-resource` exists

### Task 4: Enhance bookmark styles for dark mode
- File: `/home/aldo/dev/06-apps-neo-brutalist-home/config/custom.css`
- Before line 219 (before `/* ===== BOOKMARKS ===== */`)
- Add:
  ```css
  /* Bookmarks dark mode */
  .dark .bookmark,
  [data-theme="dark"] .bookmark {
    background: var(--nb-paper-dark) !important;
    border-color: var(--nb-border-dark) !important;
    box-shadow: 4px 4px 0 var(--nb-blue-dark) !important;
  }
  
  .dark .bookmark > div:first-child,
  [data-theme="dark"] .bookmark > div:first-child {
    background: var(--nb-lime-dark) !important;
    border-right-color: var(--nb-border-dark) !important;
    color: var(--nb-ink-dark) !important;
  }
  
  .dark .bookmark a,
  .dark .bookmark-name,
  [data-theme="dark"] .bookmark a,
  [data-theme="dark"] .bookmark-name {
    color: var(--nb-ink-dark) !important;
  }
  
  .dark .bookmark-description,
  [data-theme="dark"] .bookmark-description {
    color: #a0a0b0 !important;
  }
  ```
- Verification: Search for `.dark .bookmark` in file

### Task 5: Improve footer dark theme
- File: `/home/aldo/dev/06-apps-neo-brutalist-home/config/custom.css`
- Before line 355 (before `/* Footer styling – neon‑brutalist */`)
- Replace existing `#footer` section with enhanced version:
  ```css
  /* Footer styling – neon‑brutalist */
  #footer {
    background: var(--nb-paper-dark) !important;
    border-top: var(--nb-border-dark) !important;
    box-shadow: 4px 4px 0 var(--nb-neon-dark) !important;
    padding: 1.5rem !important;        /* More breathing room */
    text-align: center !important;
    color: var(--nb-ink-dark) !important;
    position: relative !important;
    border-bottom: var(--nb-border-dark) !important;
  }
  
  #footer::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--nb-lime-dark), transparent);
    opacity: 0.6;
  }
  
  #footer a {
    color: var(--nb-ink-dark) !important;
    text-decoration: none !important;
    font-weight: 700 !important;
    padding: 0.25rem 0.5rem !important;
    border-radius: 0 !important;
    display: inline-block !important;
    transition: all 0.15s ease !important;
  }
  
  #footer a:hover {
    background: var(--nb-lime-dark) !important;
    color: var(--nb-paper-dark) !important;
    box-shadow: 2px 2px 0 var(--nb-neon-dark) !important;
    transform: translate(-1px, -1px) !important;
  }
  ```
- Verification: Check for `#footer::before` and enhanced `#footer` styles

### Task 6: Add focus and accessibility improvements for dark mode
- File: `/home/aldo/dev/06-apps-neo-brutalist-home/config/custom.css`
- Before line 346 (before `/* ===== FOCUS STATES ===== */`)
- Add after focus section:
  ```css
  /* Enhanced focus states for dark mode */
  .dark a:focus-visible,
  .dark button:focus-visible,
  .dark input:focus-visible,
  [data-theme="dark"] a:focus-visible,
  [data-theme="dark"] button:focus-visible,
  [data-theme="dark"] input:focus-visible {
    outline: 3px solid var(--nb-lime-dark) !important;
    outline-offset: 2px !important;
    box-shadow: 0 0 8px var(--nb-lime-dark) !important;
  }
  
  /* High contrast status badges in dark mode */
  .dark .docker-status,
  [data-theme="dark"] .docker-status {
    background: var(--nb-ink-dark) !important;
    color: var(--nb-paper-dark) !important;
    border-color: var(--nb-ink-dark) !important;
  }
  
  .dark .docker-status-running,
  .dark .docker-status-healthy,
  [data-theme="dark"] .docker-status-running,
  [data-theme="dark"] .docker-status-healthy {
    background: var(--status-success) !important;
    color: var(--nb-paper-dark) !important;
    box-shadow: 0 0 6px var(--status-success) !important;
  }
  
  .dark .docker-status-stopped,
  [data-theme="dark"] .docker-status-stopped {
    background: var(--status-error) !important;
    color: var(--nb-paper-dark) !important;
    box-shadow: 0 0 6px var(--status-error) !important;
  }
  
  .dark .docker-status-unknown,
  [data-theme="dark"] .docker-status-unknown {
    background: #52525b !important;
    color: var(--nb-paper-dark) !important;
  }
  ```
- Verification: Search for `.dark .docker-status-running`

### Task 7: Add theme switcher button styles
- File: `/home/aldo/dev/06-apps-neo-brutalist-home/config/custom.css`
- Before line 399 (after `/* Hide information widget label */`)
- Add:
  ```css
  /* Theme switcher button (light/dark toggle) */
  #theme-switcher {
    position: fixed !important;
    top: 1rem !important;
    right: 1rem !important;
    z-index: 1000 !important;
    background: var(--nb-paper-dark) !important;
    border: var(--nb-border-dark) !important;
    border-radius: 0 !important;
    box-shadow: 4px 4px 0 var(--nb-neon-dark) !important;
    padding: 0.75rem !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 48px !important;
    height: 48px !important;
    transition: all 0.15s ease !important;
  }
  
  #theme-switcher:hover {
    transform: translate(-2px, -2px) !important;
    box-shadow: 6px 6px 0 var(--nb-purple-dark) !important;
    background: var(--nb-lime-dark) !important;
  }
  
  #theme-switcher svg {
    width: 24px !important;
    height: 24px !important;
    fill: var(--nb-ink-dark) !important;
  }
  
  /* Hide in dark mode when already dark */
  .dark #theme-switcher {
    opacity: 0.7 !important;
  }
  ```
- Verification: Check for `#theme-switcher` in file

## Tests / validation

### CSS syntax validation
- Command: `cd /home/aldo/dev/06-apps-neo-brutalist-home && stylelint config/custom.css --severity error || true`
- Expected: No syntax errors, CSS parse success

### Visual regression test simulation
- Command: `cd /home/aldo/dev/06-apps-neo-brutalist-home && npm run build-css 2>/dev/null || echo "No build step defined"`
- Expected: Build process completes without errors

### Component presence verification
- Command: `grep -c ".dark li.service" /home/aldo/dev/06-apps-neo-brutalist-home/config/custom.css`
- Expected: At least 1 instance

### Dark mode token check
- Command: `grep -n "var(--nb-lime-dark)" /home/aldo/dev/06-apps-neo-brutalist-home/config/custom.css`
- Expected: At least 5 instances across file

## Risks, tradeoffs, and open questions

### Risks
- **Variable scope**: Overriding existing dark mode variables may break existing layout
- **Performance**: Excessive dark mode selectors could increase CSS size
- **Maintainability**: Large number of `.dark` selectors make file hard to edit

### Tradeoffs
- **Design fidelity vs. completeness**: Limited time means we'll enhance core components but leave some edge cases (status badges, dialogs)
- **Legacy browser support**: Using CSS variables requires modern browser but project already assumes this
- **File size vs. quality**: More dark mode rules increase CSS size but improve user experience

### Open questions
- Should we add a CSS custom property for background texture/pattern for dark mode?
- Are there any third-party widget components that override our dark mode styles?
- Does the application have a preference detection system (OS theme) that we need to respect?
- Should we add dark mode toggle persistence (localStorage) to the theme switcher?

## References
- AGENTS.md: Minimal changes to templates only, avoid editing runtime dirs
- Neobrutalist design principles: sharp borders, bold shadows, high contrast
- WCAG AA contrast requirements: 4.5:1 for normal text, 3:1 for large text
- Existing custom.css structure and variable naming conventions