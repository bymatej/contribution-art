#!/usr/bin/env python3
import subprocess
import datetime
import os

def run(cmd, env=None):
    """Run a shell command, printing it first for logging."""
    print("Running:", cmd)
    subprocess.run(cmd, shell=True, check=True, env=env)

def main():
    ############# DATE RANGE SETUP #############
    today = datetime.date.today()
    offset = (today.weekday() - 5) % 7  
    last_saturday = today - datetime.timedelta(days=offset)
    end_date = last_saturday
    start_date = end_date - datetime.timedelta(days=370)
    total_days = (end_date - start_date).days + 1  # should be 371
    print(f"Generating commit art from {start_date} to {end_date} ({total_days} days)")

    ############# PATTERN SETUP #############
    # Define letter patterns for M, A, T, E, and J.
    m = [
        [1, 0, 0, 0, 1],
        [1, 1, 0, 1, 1],
        [1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
    ]
    a = [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
    ]
    t = [
        [1, 1, 1, 1, 1],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
    ]
    e = [
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [1, 1, 1, 1, 0],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [1, 1, 1, 1, 1],
    ]
    j = [
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 1, 0],
        [0, 1, 1, 0, 0],
    ]
    letter_patterns = {
        "M": m,
        "A": a,
        "T": t,
        "E": e,
        "J": j,
    }

    def build_pattern(message):
        """Build a 7-row matrix for a given message."""
        grid_rows = 7
        grid = [[] for _ in range(grid_rows)]
        for i, letter in enumerate(message):
            pattern = letter_patterns[letter]
            for r in range(grid_rows):
                grid[r].extend(pattern[r])
            if i != len(message) - 1:
                # Add a gap column between letters
                for r in range(grid_rows):
                    grid[r].append(0)
        return grid

    message = "MATEJ"
    base_pattern = build_pattern(message)
    pattern_width = len(base_pattern[0])
    print(f'Base pattern width for "{message}": {pattern_width} columns')

    grid_rows = 7
    combined = [[] for _ in range(grid_rows)]
    repeats = (53 // pattern_width) + 2  
    for i in range(repeats):
        pat = build_pattern(message)
        if i > 0:
            for r in range(grid_rows):
                combined[r].append(0)
        for r in range(grid_rows):
            combined[r].extend(pat[r])
    full_pattern = [row[:53] for row in combined]

    # Switch to the already created 'art' branch
    run("git checkout art")

    filename = "art.txt"
    with open(filename, "w") as f:
        f.write("MATEJ Commit Art\n")
    run("git add " + filename)

    # Initial commit to the branch
    initial_date = (start_date - datetime.timedelta(days=1)).strftime("%Y-%m-%dT12:00:00")
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = initial_date
    env["GIT_COMMITTER_DATE"] = initial_date
    run('git commit -m "Initial commit for commit art"', env)

    # Create back-dated commits for the pattern
    day_index = 0
    current_date = start_date
    while current_date <= end_date:
        col = day_index // 7
        row = day_index % 7
        if full_pattern[row][col] == 1:
            print(f"Creating commit for {current_date} (pattern on)")
            with open(filename, "a") as f:
                f.write(f"Commit for {current_date}\n")
            run("git add " + filename)
            commit_date = current_date.strftime("%Y-%m-%dT12:00:00")
            env["GIT_AUTHOR_DATE"] = commit_date
            env["GIT_COMMITTER_DATE"] = commit_date
            run(f'git commit -m "Commit for {current_date}"', env)
        else:
            print(f"Skipping commit for {current_date} (pattern off)")
        current_date += datetime.timedelta(days=1)
        day_index += 1

    # Update the remote URL with token
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if token and repo:
        remote_url = f"https://x-access-token:{token}@github.com/{repo}.git"
        run("git remote set-url origin " + remote_url)

        # Force-push the already created branch
        run("git push origin art --force")
    else:
        print("GITHUB_TOKEN or GITHUB_REPOSITORY not set!")

if __name__ == "__main__":
    main()