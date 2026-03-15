"""
Reddit Intelligence MCP Server
===============================
Community intelligence via Reddit's public JSON API. Six read-only tools
for searching posts, reading threads, and analyzing communities.

No authentication required. Uses Reddit's public .json endpoints.
Rate limit: ~30 req/min (sufficient for agentic research).

Usage:
    python wave/tools/ai/mcp_servers/reddit_intelligence_mcp.py
"""

import json
import time
from datetime import datetime, timezone
from typing import Any

import requests
from fastmcp import FastMCP

mcp = FastMCP(
    "RedditIntelligence",
    version="1.0.0",
    instructions=(
        "Community intelligence via Reddit. Use reddit_search to find "
        "discussions about any topic across Reddit or within specific "
        "subreddits. Use reddit_top_posts for trending content. Use "
        "reddit_post_detail to deep-read a specific thread with comments. "
        "Use reddit_subreddit_info for community health metrics."
    ),
)

_SESSION = requests.Session()
_SESSION.headers.update({"User-Agent": "ElementsIntelligence/1.0"})
_LAST_REQUEST = 0.0


def _get(url: str, params: dict | None = None) -> dict:
    """Rate-limited GET returning parsed JSON."""
    global _LAST_REQUEST
    elapsed = time.monotonic() - _LAST_REQUEST
    if elapsed < 2.0:
        time.sleep(2.0 - elapsed)
    _LAST_REQUEST = time.monotonic()
    resp = _SESSION.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def _ts(utc: float) -> str:
    """Convert UTC timestamp to ISO 8601 string."""
    return datetime.fromtimestamp(utc, tz=timezone.utc).isoformat()


def _post_summary(data: dict) -> dict:
    """Extract standard fields from a Reddit post JSON object."""
    return {
        "title": data.get("title", ""),
        "url": f"https://reddit.com{data.get('permalink', '')}",
        "subreddit": data.get("subreddit", ""),
        "score": data.get("score", 0),
        "num_comments": data.get("num_comments", 0),
        "created_utc": _ts(data.get("created_utc", 0)),
        "selftext_preview": (data.get("selftext") or "")[:500],
        "author": data.get("author", "[deleted]"),
    }


# ─────────────────────────────────────────────
# TOOLS
# ─────────────────────────────────────────────


@mcp.tool(annotations={"readOnlyHint": True})
def reddit_search(
    query: str,
    subreddit: str = "",
    sort: str = "relevance",
    time_filter: str = "all",
    limit: int = 10,
) -> str:
    """Search Reddit posts by query. Optionally scope to a subreddit.

    Args:
        query: Search terms (e.g., "Claude Code MCP server setup").
        subreddit: Optional subreddit to search within (e.g., "ClaudeAI").
        sort: One of: relevance, hot, top, new, comments.
        time_filter: One of: hour, day, week, month, year, all.
        limit: Max results (1-25).
    """
    try:
        limit = max(1, min(limit, 25))
        sub = subreddit if subreddit else "all"
        url = f"https://www.reddit.com/r/{sub}/search.json"
        params: dict[str, Any] = {
            "q": query, "sort": sort, "t": time_filter,
            "limit": limit, "restrict_sr": "1" if subreddit else "0",
        }
        data = _get(url, params)
        posts = [_post_summary(p["data"]) for p in data["data"]["children"]]
        return json.dumps({"query": query, "subreddit": sub, "results": posts})
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool(annotations={"readOnlyHint": True})
def reddit_top_posts(
    subreddit: str,
    time_filter: str = "week",
    limit: int = 10,
) -> str:
    """Get top posts from a subreddit.

    Args:
        subreddit: Subreddit name (e.g., "Python", "ClaudeAI").
        time_filter: One of: hour, day, week, month, year, all.
        limit: Max results (1-25).
    """
    try:
        limit = max(1, min(limit, 25))
        url = f"https://www.reddit.com/r/{subreddit}/top.json"
        data = _get(url, {"t": time_filter, "limit": limit})
        posts = [_post_summary(p["data"]) for p in data["data"]["children"]]
        return json.dumps({"subreddit": subreddit, "time_filter": time_filter, "results": posts})
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool(annotations={"readOnlyHint": True})
def reddit_subreddit_info(subreddit: str) -> str:
    """Get subreddit stats: subscribers, description, rules, activity.

    Args:
        subreddit: Subreddit name (e.g., "Python").
    """
    try:
        about = _get(f"https://www.reddit.com/r/{subreddit}/about.json")
        d = about["data"]
        rules_list = []
        try:
            rules = _get(f"https://www.reddit.com/r/{subreddit}/about/rules.json")
            for r in rules.get("rules", []):
                rules_list.append({
                    "name": r.get("short_name", ""),
                    "description": r.get("description", "")[:200],
                })
        except Exception:
            pass
        return json.dumps({
            "name": d.get("display_name", ""),
            "title": d.get("title", ""),
            "description": (d.get("public_description") or "")[:500],
            "subscribers": d.get("subscribers", 0),
            "active_accounts": d.get("accounts_active", 0),
            "created_utc": _ts(d.get("created_utc", 0)),
            "over18": d.get("over18", False),
            "rules": rules_list,
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool(annotations={"readOnlyHint": True})
def reddit_post_detail(
    post_url_or_id: str,
    include_comments: bool = True,
    comment_limit: int = 20,
) -> str:
    """Deep-read a specific post + comment thread.

    Args:
        post_url_or_id: Full Reddit URL or post ID (e.g., "abc123").
        include_comments: Whether to include top-level comments (default True).
        comment_limit: Max comments to return (1-50, default 20).
    """
    try:
        comment_limit = max(1, min(comment_limit, 50))

        if post_url_or_id.startswith("http"):
            # Normalize URL to .json
            url = post_url_or_id.rstrip("/")
            if not url.endswith(".json"):
                url += ".json"
        else:
            url = f"https://www.reddit.com/comments/{post_url_or_id}.json"

        data = _get(url, {"limit": comment_limit, "sort": "best"})

        # Reddit returns [post_listing, comments_listing]
        post_data = data[0]["data"]["children"][0]["data"]
        result = {
            "title": post_data.get("title", ""),
            "url": f"https://reddit.com{post_data.get('permalink', '')}",
            "subreddit": post_data.get("subreddit", ""),
            "author": post_data.get("author", "[deleted]"),
            "score": post_data.get("score", 0),
            "upvote_ratio": post_data.get("upvote_ratio", 0),
            "num_comments": post_data.get("num_comments", 0),
            "created_utc": _ts(post_data.get("created_utc", 0)),
            "selftext": post_data.get("selftext", ""),
            "link_url": post_data.get("url") if not post_data.get("is_self") else None,
        }

        if include_comments:
            comments = []
            for c in data[1]["data"]["children"][:comment_limit]:
                if c["kind"] != "t1":
                    continue
                cd = c["data"]
                comments.append({
                    "author": cd.get("author", "[deleted]"),
                    "score": cd.get("score", 0),
                    "body": (cd.get("body") or "")[:1000],
                    "created_utc": _ts(cd.get("created_utc", 0)),
                })
            result["comments"] = comments

        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool(annotations={"readOnlyHint": True})
def reddit_user_profile(username: str) -> str:
    """Get user karma, account age, and activity pattern.

    Args:
        username: Reddit username (without u/ prefix).
    """
    try:
        data = _get(f"https://www.reddit.com/user/{username}/about.json")
        d = data["data"]
        return json.dumps({
            "name": d.get("name", ""),
            "link_karma": d.get("link_karma", 0),
            "comment_karma": d.get("comment_karma", 0),
            "created_utc": _ts(d.get("created_utc", 0)),
            "is_gold": d.get("is_gold", False),
            "has_verified_email": d.get("has_verified_email", False),
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool(annotations={"readOnlyHint": True})
def reddit_user_comments(
    username: str,
    sort: str = "new",
    limit: int = 10,
) -> str:
    """Get recent comments from a user.

    Args:
        username: Reddit username (without u/ prefix).
        sort: One of: new, hot, top, controversial.
        limit: Max comments (1-25).
    """
    try:
        limit = max(1, min(limit, 25))
        url = f"https://www.reddit.com/user/{username}/comments.json"
        data = _get(url, {"sort": sort, "limit": limit})
        comments = []
        for c in data["data"]["children"]:
            if c["kind"] != "t1":
                continue
            cd = c["data"]
            comments.append({
                "subreddit": cd.get("subreddit", ""),
                "post_title": cd.get("link_title", ""),
                "body": (cd.get("body") or "")[:500],
                "score": cd.get("score", 0),
                "created_utc": _ts(cd.get("created_utc", 0)),
            })
        return json.dumps({"username": username, "sort": sort, "comments": comments})
    except Exception as e:
        return json.dumps({"error": str(e)})


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
