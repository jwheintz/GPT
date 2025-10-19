# Getting Started

This guide helps you set up the project locally and begin contributing.

1) Inspect the repository root
- Look for language/build files:
  - Node: package.json
  - Python: pyproject.toml, requirements.txt, setup.py
  - Go: go.mod
  - Rust: Cargo.toml
  - Docker: Dockerfile

2) Clone the repo
```bash
git clone https://github.com/jwheintz/GPT.git
cd GPT
ls -la
```

3) Create a language-specific environment
- Node:
```bash
npm ci
```
- Python:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
- Go:
```bash
go mod download
```

4) Configuration & secrets
- If a `.env.example` exists:
```bash
cp .env.example .env
# edit .env and fill in required keys
```
- Never commit secrets; ensure `.gitignore` contains `.env`.

5) Build & run
- Build and run per project type:
```bash
# Node
npm run build
npm start

# With Docker
docker build -t gpt-app .
docker run -p 8080:8080 --env-file .env gpt-app
```

6) Tests & linters
- Run test suite and linters before pushing:
```bash
npm test
npm run lint
pytest
flake8
go test ./...
golangci-lint run
```

7) Add or run examples
- Add short examples under `examples/` or `examples/<language>/` demonstrating core behavior.
- Document how to run each example in their README.

8) Debugging tips
- Reproduce locally with verbose logs.
- Use tests to isolate failing areas.
- Temporarily add prints/logging to narrow issues.

9) Branches & PRs
- Create a feature branch:
```bash
git checkout -b feat/<short-description>
# make changes, test
git push -u origin feat/<short-description>
```
- Open PR targeting `main` (or the repo default), include testing steps and screenshots/logs if relevant.

10) Common commands
```bash
# update branch from main
git fetch origin
git rebase origin/main
# or
git merge origin/main
```

11) Contact
- If you need help, open an issue including reproduction steps and mention @jwheintz.