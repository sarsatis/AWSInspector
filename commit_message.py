import re

# Define valid commit types for conventional commits
VALID_TYPES = ['feat', 'fix', 'chore', 'docs', 'style', 'refactor', 'test', 'perf', 'build', 'ci', 'revert']

# Define the regex pattern
# ^(feat|fix|chore|...): TO3065-\d+ .+
PATTERN = re.compile(rf"^({'|'.join(VALID_TYPES)}): TO3065-\d+ .+")


def validate_commit_message(message: str) -> bool:
    """Validates the commit message against the pattern."""
    return bool(PATTERN.match(message))


# Example usage
if __name__ == "__main__":
    test_messages = [
        "feat: TO3065-12345 Initial commit",  # valid
        "fix: TO3065-98765 Bug fix",  # valid
        "foo: TO3065-12345 Some change",  # invalid type
        "feat TO3065-12345 Missing colon",  # missing colon
        "feat: TO1234-12345 Wrong project ID",  # wrong JIRA prefix
        "feat: TO3065- Commit without ID",  # missing JIRA ID number
    ]

    for msg in test_messages:
        result = validate_commit_message(msg)
        print(f"{msg} --> {'✅ Valid' if result else '❌ Invalid'}")
