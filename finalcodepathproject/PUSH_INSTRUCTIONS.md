# Push instructions

I can't create GitHub repos or push code from this sandbox (no network, no credentials). Follow these steps once on your machine.

## 1. Create the new repo on GitHub

Go to https://github.com/new and create:
- Name: `finalcodepathproject`
- Public
- **Do NOT** initialize with README, license, or .gitignore

## 2. On your computer

```bash
git clone git@github.com:OnkarSinghBajwa/ai110-module2show-pawpal-starter.git finalcodepathproject
cd finalcodepathproject
git remote set-url origin git@github.com:<your-username>/finalcodepathproject.git
```

## 3. Drop in the new files

Copy every file from this sandbox's `/home/claude/finalcodepathproject/` directory into your local `finalcodepathproject/` folder, overwriting any conflicts. The files are bundled in the artifact I'm presenting next.

## 4. Verify it runs

```bash
pip install -r requirements.txt
python main.py
python -m pytest tests/ -v
python evaluate.py
streamlit run app.py
```

You should see 12/12 tests pass and 7/7 eval cases pass.

## 5. Make several meaningful commits (the rubric checks history)

Don't squash it into one commit. Suggested split:

```bash
git add pawpal_system.py
git commit -m "feat: extend Owner/Pet/Task/Scheduler with sort, filter, recurrence, conflicts"

git add data/ retriever.py
git commit -m "feat: add TF-IDF RAG retriever and pet-care knowledge base"

git add agent.py
git commit -m "feat: add agentic plan-act-check workflow with guardrails and confidence"

git add main.py app.py
git commit -m "feat: wire CLI demo and Streamlit UI to agent + scheduler"

git add tests/ evaluate.py
git commit -m "test: add 12-case pytest suite and 7-case evaluation harness"

git add assets/ README.md model_card.md requirements.txt .gitignore
git commit -m "docs: README, model card, architecture diagram"

git push -u origin main
```

(Use `master` if your default branch is master.)

## 6. Record the Loom

Show: CLI demo (2-3 inputs), the agent answering a benign question, the guardrail blocking the chocolate question, and `python -m pytest` going green. Drop the link into the README under "Loom walkthrough."
