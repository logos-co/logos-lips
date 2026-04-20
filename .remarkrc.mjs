// Based on https://github.com/status-im/status-web/blob/07e85e1d9eddc10be47e19c11a3bc5b6d3919c47/apps/status.app/.remarkrc.mjs
import remarkGfm from 'remark-gfm'
import remarkPresetLintConsistent from 'remark-preset-lint-consistent'
import remarkPresetLintRecommended from 'remark-preset-lint-recommended'

const disabledRecommended = new Set([
  'remark-lint:list-item-bullet-indent', // Do not force one bullet indentation style.
  'remark-lint:no-blockquote-without-marker', // Allow plain wrapped quotes in imported docs.
  'remark-lint:no-undefined-references', // Permit refs resolved by external tooling/contexts.
  'remark-lint:ordered-list-marker-style', // Allow mixed ordered marker styles.
  'remark-lint:hard-break-spaces', // Do not enforce trailing-space hard-break style.
  'remark-lint:final-newline', // Do not require final newline in every file.
  'remark-lint:no-shortcut-reference-link', // Allow shortcut reference links.
  'remark-lint:no-shortcut-reference-image', // Allow shortcut reference images.
])

const disabledConsistent = new Set([
  'remark-lint:code-block-style', // Allow both fenced and indented code blocks.
  'remark-lint:list-item-content-indent', // Do not enforce one list content indent style.
  'remark-lint:ordered-list-marker-style', // Allow mixed ordered marker styles.
  'remark-lint:table-cell-padding', // Do not enforce fixed table cell padding style.
  'remark-lint:blockquote-indentation', // Allow mixed blockquote indentation styles.
])

const filteredRecommended = {
  ...remarkPresetLintRecommended,
  plugins: remarkPresetLintRecommended.plugins.filter((plugin) => {
    const entry = Array.isArray(plugin) ? plugin[0] : plugin
    const name = typeof entry === 'string' ? entry : entry?.name
    return !disabledRecommended.has(name)
  }),
}

const filteredConsistent = {
  ...remarkPresetLintConsistent,
  plugins: remarkPresetLintConsistent.plugins.filter((plugin) => {
    const entry = Array.isArray(plugin) ? plugin[0] : plugin
    const name = typeof entry === 'string' ? entry : entry?.name
    return !disabledConsistent.has(name)
  }),
}

/** @type {Array<import('unified').Plugin | import('unified').Preset>} */
const plugins = [
  remarkGfm,
  filteredConsistent,
  filteredRecommended,
  ['remark-lint-no-html', false], // Allow inline HTML in legacy/spec docs.
  ['remark-lint-file-extension', false], // Do not enforce file extension policy.
  ['remark-lint-no-literal-urls', false], // Allow raw URLs for readability.
  ['remark-lint-no-paragraph-content-indent', false], // Allow paragraph indentation variants.
  ['remark-lint-maximum-heading-length', false], // Do not cap heading length.
  ['remark-lint-maximum-line-length', false], // Do not cap line length.
  ['remark-lint-ordered-list-marker-value', false], // Do not enforce sequential list markers.
  ['remark-lint-unordered-list-marker-style', false], // Allow mixed unordered list markers.
  ['remark-lint-table-pipe-alignment', false], // Do not enforce table pipe alignment.
  ['remark-lint-heading-style', false], // Allow ATX/setext heading style mix.
  ['remark-lint-first-heading-level', false], // Do not enforce first heading level.
  ['remark-lint-list-item-indent', false], // Allow list item indentation variants.
  ['remark-lint-list-item-spacing', false], // Allow flexible blank lines in lists.
  ['remark-lint-heading-increment', false], // Do not require strict heading level increments.
  ['remark-lint-no-duplicate-headings', false], // Allow duplicate headings across document.
  ['remark-lint-no-duplicate-headings-in-section', false], // Allow duplicate headings in sections.
  ['remark-lint-no-emphasis-as-heading', false], // Allow emphasized lines used as pseudo-headings.
  ['remark-lint-emphasis-marker', false], // Allow mixed emphasis marker styles.
]

/** @type {import('unified').Preset} */
export default {
  settings: {
    emphasis: '_',
    bullet: '-',
    quote: '"',
    listItemIndent: 'one',
    rule: '-',
    incrementListMarker: false,
  },
  plugins,
}
