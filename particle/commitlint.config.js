/**
 * Commitlint Configuration for PROJECT_elements
 *
 * Enforces Conventional Commits format:
 *   <type>(<scope>): <subject>
 *
 * Examples:
 *   feat(collider): Add topology health index
 *   fix(viz): Resolve edge rendering in 2D mode
 *   docs(agent): Update onboarding protocol
 *   chore: Archive stale research files
 *
 * Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
 *
 * Scopes (optional but recommended):
 *   - collider: Standard Model of Code / Collider pipeline
 *   - viz: Visualization (app.js, modules/)
 *   - agent: .agent/ directory (tasks, registry, sprints)
 *   - aci: AI Context Intelligence tools
 *   - hsl: Holographic Socratic Layer
 *   - refinery: Context atomization
 *   - archive: Archive/cleanup operations
 */

module.exports = {
  extends: ['@commitlint/config-conventional'],

  rules: {
    // Type must be one of the conventional types
    'type-enum': [
      2,
      'always',
      [
        'feat',     // New feature
        'fix',      // Bug fix
        'docs',     // Documentation only
        'style',    // Formatting, no code change
        'refactor', // Code change that neither fixes bug nor adds feature
        'perf',     // Performance improvement
        'test',     // Adding or updating tests
        'build',    // Build system or dependencies
        'ci',       // CI configuration
        'chore',    // Other changes (archive, cleanup)
        'revert',   // Revert a commit
      ],
    ],

    // Scope is optional but should be lowercase
    'scope-case': [2, 'always', 'lower-case'],

    // Subject (description) rules
    'subject-case': [2, 'never', ['start-case', 'pascal-case', 'upper-case']],
    'subject-empty': [2, 'never'],
    'subject-full-stop': [2, 'never', '.'],

    // Header (type + scope + subject) max length
    'header-max-length': [2, 'always', 100],

    // Body rules (optional but if present, must be formatted)
    'body-leading-blank': [2, 'always'],
    'body-max-line-length': [1, 'always', 120],  // Warning only

    // Footer rules (for references like TASK-XXX)
    'footer-leading-blank': [2, 'always'],
  },

  // Help message shown on failure
  helpUrl: 'https://www.conventionalcommits.org/en/v1.0.0/',
};
