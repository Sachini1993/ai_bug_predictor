import git
import pandas as pd

repo = git.Repo("repos/flask")
commits = list(repo.iter_commits("main"))
print(f"Total commits to process: {len(commits)}")

bug_keywords = ["fix", "bug", "patch", "error", "issue", "crash", "fault"]

def is_bug_fix(message):
    msg = message.lower()
    return any(keyword in msg for keyword in bug_keywords)

records = []

for i, commit in enumerate(commits):
    if i % 200 == 0:
        print(f"Processing commit {i}/{len(commits)}...")

    # This must be OUTSIDE the "i % 200" block
    if len(commit.parents) != 1:
        continue

    parent = commit.parents[0]
    diffs = parent.diff(commit, create_patch=True)

    for diff in diffs:
        file_path = diff.b_path or diff.a_path

        if not file_path.endswith(".py"):
            continue

        # These must be INSIDE the diff loop
        lines_added = 0
        lines_deleted = 0

        try:
            for line in diff.diff.decode("utf-8", errors="ignore").split("\n"):
                if line.startswith("+") and not line.startswith("+++"):
                    lines_added += 1    # fixed typo: was "linnes_added"
                elif line.startswith("-") and not line.startswith("---"):
                    lines_deleted += 1
        except:
            continue

        records.append({
            "commit_hash": commit.hexsha[:7],
            "date": commit.committed_datetime.isoformat(),
            "author": commit.author.name,
            "file_path": file_path,
            "lines_added": lines_added,
            "lines_deleted": lines_deleted,
            "churn": lines_added + lines_deleted,
            "is_bug_fix": int(is_bug_fix(commit.message)),
            "commit_message": commit.message.strip()[:100]
        })

print(f"Extracted {len(records)} file-commit records")

df = pd.DataFrame(records)
df.to_csv("data/git_metadata.csv", index=False)   # fixed: was "datd/get_metadata.csv"

print(df.head(10))
print(f"\nBug-fix records: {df['is_bug_fix'].sum()}")
print(f"Clean records: {(df['is_bug_fix'] == 0).sum()}")
print(f"Bug ratio: {df['is_bug_fix'].mean():.1%}")