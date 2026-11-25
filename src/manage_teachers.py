import argparse
import getpass
import json
import secrets
from pathlib import Path

from teacher_auth import hash_password


TEACHERS_FILE = Path(__file__).with_name("teachers.json")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add a teacher account for the activities application."
    )
    parser.add_argument("username", help="Teacher username")
    args = parser.parse_args()

    username = args.username.strip()
    if not username:
        parser.error("username cannot be empty")
    if not username.isascii() or ":" in username:
        parser.error("username must use ASCII characters and cannot contain ':'")

    password = getpass.getpass("Teacher password (at least 12 characters): ")
    if len(password) < 12:
        parser.error("password must be at least 12 characters")
    if not password.isascii():
        parser.error("password must contain only ASCII characters")
    if password != getpass.getpass("Confirm password: "):
        parser.error("passwords do not match")

    if TEACHERS_FILE.exists():
        data = json.loads(TEACHERS_FILE.read_text(encoding="utf-8"))
    else:
        data = {"teachers": {}}
    if not isinstance(data, dict):
        parser.error("teachers.json must contain a JSON object")
    teachers = data.get("teachers")
    if not isinstance(teachers, dict):
        parser.error("teachers.json must contain a teachers object")
    if username in teachers:
        parser.error(f"teacher {username!r} already exists")

    salt = secrets.token_bytes(16)
    teachers[username] = {
        "salt": salt.hex(),
        "password_hash": hash_password(password, salt),
    }
    TEACHERS_FILE.write_text(json.dumps(data, indent=2) + "\n",
                             encoding="utf-8")
    TEACHERS_FILE.chmod(0o600)
    print(f"Added teacher {username!r} to {TEACHERS_FILE}")


if __name__ == "__main__":
    main()
