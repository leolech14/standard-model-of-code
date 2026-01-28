# Research: Neo4j local installation (Homebrew on macOS) is showing authentication rate limit error after too ma...

> **Date:** 2026-01-27 15:06:09
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:fea44029c45eb1833bb189142ad1336c0ac779968c63d11874d064a59e7f7b38`
> **Raw JSON:** `raw/20260127_150609_neo4j_local_installation__homebrew_on_macos__is_sh.json`

---

## Query

Neo4j local installation (Homebrew on macOS) is showing authentication rate limit error after too many failed login attempts. Error: 'Neo.ClientError.Security.AuthenticationRateLimit: The client has provided incorrect authentication details too many times in a row.'

How to properly reset Neo4j password and clear authentication lockout? Need exact commands for:
1. Stop Neo4j service
2. Clear auth database
3. Reset to default password
4. Restart service
5. Verify connection works

Version: Neo4j 2025.12.1 (latest Homebrew)
OS: macOS (Apple Silicon)
Install location: /opt/homebrew/Cellar/neo4j/

---

## Response

The **authentication rate limit** in Neo4j is a security mechanism that locks out access after multiple failed login attempts[6]. To resolve this on macOS with Homebrew, you'll need to stop the service, clear the authentication database, and restart.

## Step-by-step commands for macOS (Homebrew)

**1. Stop Neo4j service**

```bash
brew services stop neo4j
```

Or if that doesn't work, use:

```bash
launchctl stop homebrew.mxcl.neo4j
```

**2. Clear authentication database**

Navigate to the Neo4j data directory and remove the authentication files:

```bash
rm -rf /opt/homebrew/var/neo4j/data/dbms/auth*
```

This removes the locked-out authentication state[1][7].

**3. Start Neo4j service**

```bash
brew services start neo4j
```

**4. Reset to default credentials**

Once Neo4j restarts, it will reinitialize with default credentials (username: `neo4j`, password: `neo4j`). You can then connect:

```bash
cypher-shell -u neo4j -p neo4j
```

**5. Change the password immediately**

When you first connect, Neo4j will prompt you to change the default password:

```
:server change-password
```

Follow the prompts to set a new password[1].

**6. Verify connection**

Test the connection with your new credentials:

```bash
cypher-shell -u neo4j -p your_new_password
```

## Additional troubleshooting

If you still encounter the rate limit error, check that **no other processes are attempting to connect with incorrect credentials**[4]. For example, close any open Neo4j browser windows that might be retrying old credentials. You can also verify Neo4j is running properly with:

```bash
brew services list
```

If Neo4j appears to have crashed, check the logs:

```bash
cat /opt/homebrew/var/log/neo4j/neo4j.log
```

---

## Citations

1. https://community.neo4j.com/t/neo-clienterror-security-authenticationratelimit-the-client-has-provided-incorrect-authentication-details-too-many-times-in-a-row/28844
2. https://community.neo4j.com/t/set-or-adjust-authenticationratelimit-in-neo4j-enterprise/52545
3. https://github.com/neo4j/neo4j/issues/13456
4. https://github.com/neo4j/neo4j/issues/12904
5. https://community.neo4j.com/t/neo-clienterror-security-authenticationratelimit/2707
6. https://leanjavaengineering.wordpress.com/2015/04/16/neo4j-2-2-authentication-and-adding-extra-users/
7. https://groups.google.com/g/neo4j/c/TWU99Atvr8k

---

## Usage Stats

- Prompt tokens: 139
- Completion tokens: 427
- Total tokens: 566
