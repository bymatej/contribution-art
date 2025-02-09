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
    # We want to rebuild a commit history covering 53 full weeks (371 days).
    # Here we choose the period so that it ends on the last Saturday.
    # (GitHub’s contributions grid starts on Sunday; this ensures our mapping is correct.)
    today = datetime.date.today()
    # In Python, Monday = 0, …, Saturday = 5, Sunday = 6.
    # Compute how many days to subtract so that we land on Saturday.
    offset = (today.weekday() - 5) % 7  
    last_saturday = today - datetime.timedelta(days=offset)
    end_date = last_saturday
    start_date = end_date - datetime.timedelta(days=370)
    total_days = (end_date - start_date).days + 1  # should be 371

    print(f"Generating commit art from {start_date} to {end_date} ({total_days} days)")

    ############# PATTERN SETUP #############
    # Define letter patterns for M, A, T, E, and J.
    # Each is a 7x5 matrix (rows represent days of week, row 0 = Sunday).
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
        [0,0,  1, 0, 0],
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
        """Build a 7-row matrix for a given message.
           Each letter is 5 columns; a gap column (all 0’s) is added between letters."""
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

    # Build the base pattern for "MATEJ"
    message = "MATEJ"
    base_pattern = build_pattern(message)
    pattern_width = len(base_pattern[0])
    print(f'Base pattern width for "{message}": {pattern_width} columns')

    # We want a full grid that is exactly 53 columns wide (one column per week).
    # To cover 53 columns, we repeat the base pattern as many times as needed and then slice.
    grid_rows = 7
    combined = [[] for _ in range(grid_rows)]
    # Calculate a number of repeats that will surely exceed 53 columns.
    repeats = (53 // pattern_width) + 2  
    for i in range(repeats):
        pat = build_pattern(message)
        if i > 0:
            # Insert a gap column between repeats
            for r in range(grid_rows):
                combined[r].append(0)
        for r in range(grid_rows):
            combined[r].extend(pat[r])
    # Slice each row to exactly 53 columns.
    full_pattern = [row[:53] for row in combined]
    actual_width = len(full_pattern[0])
    print(f"Full pattern dimensions: {grid_rows} rows x {actual_width} columns")

    ############# REBUILD THE ART BRANCH #############
    # We now re-create an orphan branch (named "art") so that we control its entire commit history.
    branch_name = "art"
    run("git checkout --orphan " + branch_name)
    run("git rm -rf .")

    # Create an initial file that will be modified by each commit.
    filename = "art.txt"
    with open(filename, "w") as f:
        f.write("MATEJ Commit Art\n")
    run("git add " + filename)
    # Set the initial commit date to one day before our start_date.
    initial_date = (start_date - datetime.timedelta(days=1)).strftime("%Y-%m-%dT12:00:00")
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = initial_date
    env["GIT_COMMITTER_DATE"] = initial_date
    run('git commit -m "Initial commit for commit art"', env)

    ############# CREATE BACK-DATED COMMITS #############
    # We now iterate over each day in our period. We assume that the start_date is a Sunday,
    # so the cell at row 0, col 0 corresponds to start_date (Sunday), row 1 to Monday, etc.
    day_index = 0
    current_date = start_date
    while current_date <= end_date:
        # Map the day_index to grid coordinates.
        col = day_index // 7  # week index
        row = day_index % 7   # day-of-week (0 = Sunday, …, 6 = Saturday)
        if full_pattern[row][col] == 1:
            print(f"Creating commit for {current_date} (pattern on)")
            # Append a line to the file so there is a change.
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

    ############# FORCE-PUSH THE NEW HISTORY #############
    run("git push origin " + branch_name + " --force")
    print("Commit art generation complete.")

if __name__ == "__main__":
    main()
