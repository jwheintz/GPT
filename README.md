# Proficient Programming Languages

Short description
- A repository listing programming languages the AI is proficient in.

Status
- Project status: Active
- Supported languages: See [PROFICIENT_LANGUAGES.md](PROFICIENT_LANGUAGES.md)
- Roadmap: Expand list with code examples for each language.

Quick links
- Getting started: docs/GETTING_STARTED.md
- Contributing: CONTRIBUTING.md
- Issues: https://github.com/jwheintz/GPT/issues
- Full Language List: [PROFICIENT_LANGUAGES.md](PROFICIENT_LANGUAGES.md)

Quickstart (generic)
1. Prerequisites
   - Git >= 2.20
   - Node.js (if applicable): node >= 16 and npm or yarn
   - Python (if applicable): python >= 3.8 and pip
   - Go (if applicable): go >= 1.18
   - Docker (optional): docker >= 20.x

2. Clone the repo
```bash
git clone https://github.com/jwheintz/GPT.git
cd GPT
```

3. Identify language / build system
- package.json → Node.js / TypeScript
- pyproject.toml, requirements.txt or setup.py → Python
- go.mod → Go
- Cargo.toml → Rust
- Dockerfile → containerized app

4. Common install / run commands (pick the block matching this repo)
- Node.js
```bash
npm ci
npm run build    # if present
npm start        # or `npm run dev`
npm test
```
- Python (venv)
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest
```
- Go
```bash
go mod download
go build ./...
go test ./...
```
- Docker
```bash
docker build -t gpt-app .
docker run -p 8080:8080 --env-file .env gpt-app
```

5. Run tests
- Look for tests/ or __tests__/ or a Makefile target `test` and run accordingly:
```bash
npm test
pytest
go test ./...
make test
```

6. Example usage
- Replace the example below with repo-specific instructions:
```bash
# Start the app, then check health
npm start
curl http://localhost:8080/health
```

7. Need help?
- Open an issue at https://github.com/jwheintz/GPT/issues and include:
  - OS/version
  - Steps to reproduce
  - Logs or error output
