"""Reject tracked local connection bundles and verify their ignore rules."""
import pathlib
import subprocess
import sys

root = pathlib.Path(__file__).resolve().parents[2]
tracked = subprocess.check_output(
    ["git", "ls-files", "-z"], cwd=root
).decode("utf-8").split("\0")
private_names = {
    "1c_bridge_client_config.json",
    "1c_bridge_client_key.env",
    "ИНСТРУКЦИЯ (для агента).md",
}
errors = []
for name in filter(None, tracked):
    path = pathlib.PurePosixPath(name)
    if (
        path.name in private_names
        or path.name == ".env"
        or path.name.startswith(".env.")
        or path.suffix.lower() in {".env", ".key", ".pem", ".pfx", ".p12"}
        or any(part in {".1cbridge", "secrets"} for part in path.parts)
    ):
        errors.append(f"Private/local file is tracked: {name}")

for name in sorted(private_names):
    for candidate in [name, f"sample-project/{name}"]:
        result = subprocess.run(
            ["git", "check-ignore", "--no-index", "-q", candidate], cwd=root
        )
        if result.returncode != 0:
            errors.append(f"Missing ignore rule: {candidate}")

for name in ["README.md", "LICENSE", "SECURITY.md", "CONTRIBUTING.md"]:
    if not (root / name).is_file():
        errors.append(f"Required file is missing: {name}")

if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)
print("Repository hygiene passed. This is not a full secret scan or crypto audit.")
