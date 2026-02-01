# Research: Neo4j local installation (Homebrew macOS) authentication troubleshooting:

SYMPTOMS:
- Neo4j Browser...

> **Date:** 2026-01-27 15:36:22
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:999473135883d4664e04e71aeec352b206890c03542d276db73d9ac91bd71a83`
> **Raw JSON:** `raw/20260127_153622_neo4j_local_installation__homebrew_macos__authenti.json`

---

## Query

Neo4j local installation (Homebrew macOS) authentication troubleshooting:

SYMPTOMS:
- Neo4j Browser loads successfully at http://localhost:7474
- When connecting to neo4j://localhost:7687 with username 'neo4j' and password 'neo4j'
- Error: Neo.ClientError.Security.Unauthorized - authentication failure

WHAT WE DID:
- Installed Neo4j 2025.12.1 via Homebrew
- Cleared auth files: rm -rf /opt/homebrew/var/neo4j/data/dbms/auth*
- Ran: neo4j-admin dbms set-initial-password elements2026
- Restarted service multiple times
- Logs show 'Started' successfully, Bolt on 7687, HTTP on 7474

QUESTION:
1. After clearing auth files and restarting, should default be neo4j/neo4j or the password we set via neo4j-admin?
2. How to verify what the actual password is?
3. Command to manually reset to known password?
4. Common causes of 'Unauthorized' even with correct credentials?
5. Does neo4j-admin set-initial-password work AFTER first start (or only before)?

Need exact Homebrew macOS commands to fix authentication and get connected.

---

## Response

**After clearing auth files and running `neo4j-admin dbms set-initial-password elements2026`, the password should be `elements2026` (not the default `neo4j`), but Homebrew Neo4j installs often ignore this due to config issues or service state, defaulting back to `neo4j/neo4j`.[1][2][3]**

### Exact Homebrew macOS Commands to Fix Authentication
Run these **in order** on macOS with Apple Silicon (adjust `/usr/local` for Intel):

1. **Stop the service:**
   ```
   brew services stop neo4j
   ```

2. **Clear auth and migrate config (fixes common Homebrew validation errors):**
   ```
   rm -rf /opt/homebrew/var/neo4j/data/dbms/auth*
   neo4j-admin server migrate-configuration --from=/opt/homebrew/Cellar/neo4j/2025.12.1/libexec/conf/neo4j.conf
   ```

3. **Set initial password cleanly:**
   ```
   neo4j-admin dbms set-initial-password elements2026 --database=system
   ```

4. **Start in console mode first (verify logs):**
   ```
   neo4j console
   ```
   - Watch for auth errors. Press Ctrl+C after confirming "Bolt enabled on 7687" and "HTTP enabled on 7474".
   - Test connection: `cypher-shell -u neo4j -p elements2026`

5. **If console works, start service:**
   ```
   brew services start neo4j
   ```

6. **Connect via Browser:** http://localhost:7474 → `neo4j` / `elements2026`

### Answers to Your Questions
1. **Should be the set password (`elements2026`), not default** - but Homebrew often reverts to `neo4j/neo4j` due to config migration issues or partial auth persistence.[1][3]

2. **Verify actual password:**
   ```
   cypher-shell -u neo4j -p neo4j  # Test default first
   # OR
   cypher-shell -u neo4j -p elements2026  # Test your set password
   ```
   Success shows `:server switch to: 'system'` prompt.[1]

3. **Manual reset command:**
   ```
   neo4j stop
   rm -rf /opt/homebrew/var/neo4j/data/dbms/auth*
   neo4j-admin dbms set-initial-password newpassword123 --database=system
   neo4j start
   ```

4. **Common 'Unauthorized' causes (even with correct creds):**
   - Config strict validation blocks start: `wrapper.java.additional` errors[2][3]
   - Auth file corruption/regeneration[1]
   - Service not fully restarted (stale Bolt connector)[1]
   - `dbms.security.auth_enabled=true` but mismatched userdb[1]
   - Browser cache: Clear site data for localhost:7474

5. **`neo4j-admin set-initial-password` works AFTER first start** - but requires auth files cleared first. It targets empty/no-auth state.[1]

### If Still Fails
**Nuclear option (loses data):**
```
brew services stop neo4j
rm -rf /opt/homebrew/var/neo4j/data/
brew services start neo4j
```
Browser prompts for new password at http://localhost:7474 (defaults to `neo4j/neo4j` initially).[1]

**Check logs:** `tail -f /opt/homebrew/var/neo4j/log/neo4j.log` during start for auth errors.

---

## Citations

1. https://community.neo4j.com/t/connect-neo-clienterror-security-unauthorized-the-client-is-unauthorized-due-to-authentication-failure/11801
2. https://github.com/Homebrew/homebrew-core/issues/130843
3. https://github.com/Homebrew/homebrew-core/issues/114553
4. https://community.neo4j.com/t/authentication-error-in-neo4j/61107
5. https://tarnaeluin.houseofbeor.net/working-with-graph-databases-and-neo4j/

---

## Usage Stats

- Prompt tokens: 256
- Completion tokens: 781
- Total tokens: 1037
