"""
Cellshift — Daily Business Monitor Agent
Runs as a scheduled task (via Claude scheduled tasks or cron).
Checks: app uptime, GitHub activity, basic metrics.
Sends summary report.
"""

import requests
import json
from datetime import datetime, timedelta

# ─── CONFIG ───
APP_URL = "https://cellshift-2cynfq4cvdqktk4suwqwqh.streamlit.app"
GITHUB_REPO = "YOUR_USERNAME/cellshift"       # Update after GitHub setup
GITHUB_TOKEN = ""  # Optional: for private repos

# ─── CHECKS ───
def check_uptime():
    """Ping the Streamlit app and check response."""
    try:
        r = requests.get(APP_URL, timeout=15)
        return {
            "status": "UP" if r.status_code == 200 else "DOWN",
            "response_time_ms": round(r.elapsed.total_seconds() * 1000),
            "status_code": r.status_code
        }
    except Exception as e:
        return {"status": "DOWN", "error": str(e), "response_time_ms": -1}


def check_github_activity():
    """Check recent commits and open issues."""
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    try:
        # Recent commits
        commits_url = f"https://api.github.com/repos/{GITHUB_REPO}/commits"
        r = requests.get(commits_url, headers=headers, params={"per_page": 5}, timeout=10)
        commits = r.json() if r.status_code == 200 else []

        recent_commits = []
        for c in commits[:5]:
            recent_commits.append({
                "message": c.get("commit", {}).get("message", "")[:80],
                "date": c.get("commit", {}).get("author", {}).get("date", ""),
                "author": c.get("commit", {}).get("author", {}).get("name", "")
            })

        # Days since last commit
        last_commit_date = None
        if recent_commits and recent_commits[0].get("date"):
            last_commit_date = datetime.fromisoformat(recent_commits[0]["date"].replace("Z", "+00:00"))
            days_since = (datetime.now(last_commit_date.tzinfo) - last_commit_date).days
        else:
            days_since = -1

        # Open issues
        issues_url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
        r2 = requests.get(issues_url, headers=headers, params={"state": "open", "per_page": 5}, timeout=10)
        open_issues = len(r2.json()) if r2.status_code == 200 else 0

        return {
            "recent_commits": recent_commits,
            "days_since_last_commit": days_since,
            "open_issues": open_issues,
            "status": "ACTIVE" if days_since <= 7 else "STALE" if days_since <= 14 else "INACTIVE"
        }
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}


def generate_report():
    """Generate the daily monitoring report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    uptime = check_uptime()
    github = check_github_activity()

    report = f"""
╔══════════════════════════════════════════════════════════╗
║           CELLSHIFT — DAILY MONITOR REPORT              ║
║           {now}                              ║
╠══════════════════════════════════════════════════════════╣

1. APP STATUS
   URL: {APP_URL}
   Status: {uptime['status']}
   Response Time: {uptime.get('response_time_ms', 'N/A')}ms
   {"⚠ ACTION NEEDED: App is DOWN!" if uptime['status'] == 'DOWN' else "✓ App is healthy"}

2. DEVELOPMENT ACTIVITY
   Status: {github.get('status', 'N/A')}
   Days Since Last Commit: {github.get('days_since_last_commit', 'N/A')}
   Open Issues: {github.get('open_issues', 'N/A')}
   {"⚠ No commits in 7+ days — ship something!" if github.get('days_since_last_commit', 0) > 7 else "✓ Active development"}

   Recent Commits:
"""
    for c in github.get("recent_commits", [])[:3]:
        report += f"   • {c.get('date', '')[:10]} — {c.get('message', 'N/A')}\n"

    report += f"""
3. WEEKLY PRIORITIES
   □ Check user signups / analytics dashboard
   □ Review and respond to any support emails
   □ Ship at least 1 improvement or bug fix
   □ Post 3x on LinkedIn (content calendar)
   □ Send 20 cold emails (lead gen playbook)
   □ Follow up with warm leads

4. KEY METRICS TO TRACK
   □ Total registered users (target: +25/week)
   □ Daily active transformations
   □ Conversion rate: Free → Pro
   □ Churn rate (Pro/Business)
   □ NPS score from feedback widget

╚══════════════════════════════════════════════════════════╝
"""
    return report


if __name__ == "__main__":
    report = generate_report()
    print(report)

    # Save to file
    filename = f"monitor_report_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(filename, "w") as f:
        f.write(report)
    print(f"Report saved: {filename}")
