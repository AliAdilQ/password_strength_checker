# Contributing to Password Strength Checker

Thank you for helping make password security more approachable. Bug fixes, accessibility improvements, documentation, and focused features are welcome.

## Getting started

1. Fork [AliAdilQ/password_strength_checker](https://github.com/AliAdilQ/password_strength_checker).
2. Clone your fork and follow the installation instructions in [README.md](README.md).
3. Create a feature branch:

   ```bash
   git checkout -b feature/describe-your-change
   ```

4. Make a focused change. Keep route handling, analysis services, templates, and frontend behavior separate.
5. Run the test suite:

   ```bash
   pytest
   ```

6. For interface changes, inspect desktop and mobile layouts in both themes. Check keyboard navigation, password visibility, generator options, and relevant admin flows. Update screenshots when the interface changes substantially.
7. Commit and push your changes:

   ```bash
   git add .
   git commit -m "Describe the user-visible improvement"
   git push origin feature/describe-your-change
   ```

8. Open a pull request against the original repository. Describe the problem, the resulting behavior, and how you verified the change. Link a related issue if one exists.

## Privacy is a requirement

- Never store, hash, log, print, cache, or echo passwords being checked or generated.
- Keep analytics strictly limited to the documented metadata allowlist.
- Preserve CSRF protection on admin forms and browser analytics submissions.
- Use synthetic inputs for tests and screenshots. Hide generated passwords in screenshots.
- Keep Python and JavaScript scoring behavior aligned; shared rule data lives in `app/static/data/scoring-rules.json`.
- Use `crypto.getRandomValues()` or Python's `secrets` for security-sensitive randomness.
- Do not commit `.env`, local databases, virtual environments, caches, or credentials beyond the explicitly documented local demo account.

## Reporting bugs

Open an issue with reproduction steps, expected and actual behavior, Python/browser versions, and non-sensitive screenshots when useful. Never include a real password, session cookie, `.env` file, or private account data in an issue or pull request.

If you find a security vulnerability, use GitHub's private vulnerability reporting when it is enabled, or contact the maintainer privately before publishing exploit details.

Contributions are provided under the project's [MIT License](LICENSE).
