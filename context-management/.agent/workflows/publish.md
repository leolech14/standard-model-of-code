---
description: Verify and publish the codebase to the remote repository
---

1. Run the audit to ensure system health.
   ```bash
   python3 cli.py audit
   ```

2. Check git status to see what will be committed.
   ```bash
   git status
   ```

3. Add all changes.
   ```bash
   git add .
   ```

4. Commit with a descriptive message.
   ```bash
   git commit -m "feat: Unified Data Layer & Spectrometer V2"
   ```

5. Push to the main branch.
   ```bash
   git push origin main
   ```
