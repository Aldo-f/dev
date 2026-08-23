# Selector Harvest — gethomepage v1.13.2 (from shipped JS chunks, 2026-08-23)

Source: all 15 `/_next/static/chunks/*.js` of the live deployment
(`/tmp/hp-chunks/`, concatenated `all.js`). These are the app's own semantic,
version-stable class names (not utility chains).

## Semantic hooks (preferred targets)

| Hook | Role |
|---|---|
| `.service-container` | one service card row (`relative flex flex-row w-full`) |
| `.service-name` | card text area (`flex-1 px-2 py-2 … z-10`) |
| `.service-title-text` | title wrapper (`flex-1 flex items-center justify-between rounded-r-md`) |
| `.service-description` | description line (`text-theme-500 … text-xs font-light`) |
| `.service-group-name` | group heading (`flex text-theme-800 … text-xl font-medium`) |
| `.service-group-icon` | group heading icon (`shrink-0 mr-2 w-7 h-7`) |
| `.bookmark-text` / `.bookmark-name` / `.bookmark-group-name` / `.bookmark-icon` | bookmark tile parts |
| `.information-widget-resource` | top-bar info widget block (`flex-none … py-1.5`, takes `additionalClassNames`) |
| `.information-widget-label` | widget label line (`pt-1 text-center … text-xs`) |
| `.widget-inner` / `.widget-inner-text` / `.widget-inner-icon` | widget internals |
| generic card surface | `rounded-md shadow-md shadow-theme-900/10 dark:shadow-theme-900/20 bg-theme-100/20 dark:bg-white/5 p-2 pl-3 pr-3` |

## Theming notes

- App palette is CSS-variable driven (`theme-*` utilities read custom props) →
  overriding the underlying variables is lower-risk than fighting per-element.
- Cards/bookmarks are **rounded + soft shadows** by default; neobrutalist look
  = square corners, `border: 2px solid #000`, `box-shadow: 4px 4px 0 #000`,
  pressed hover via translate.
- Status dots are separate elements; do not recolor (plan D6).
