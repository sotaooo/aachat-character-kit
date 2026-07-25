# aachat Character Kit

A small, agent-neutral kit for making aachat Level 4/5 character masters.
Codex, aachat, or another image-capable agent can use the same four references,
one specification, and one approval flow.

## Start

1. Read [`SKILL.md`](SKILL.md).
2. Install the only tool dependency: `python3 -m pip install -r requirements.txt`.
3. Build a prompt:

   ```bash
   python3 scripts/build_prompt.py \
     --mode concept --level 4 \
     --brief "A monsoon observatory carried as a living instrument"
   ```

   Optional examples and LCD correction wording are in
   [`references/PROMPT_GUIDE.md`](references/PROMPT_GUIDE.md).

4. Generate into `.work/candidates/`, then inspect and iterate.
5. Record a system pass only after mechanical and visual QA:

   ```bash
   python3 scripts/kit.py system-pass .work/candidates/example.png --visual-pass
   ```

6. Show the system-approved image to a human. Only after explicit approval:

   ```bash
   python3 scripts/kit.py approve .work/system-approved/example.png \
     --name example.png --human-approved
   ```

`production/` contains opaque RGB masters only. `derivatives/transparent/`
contains optional RGBA derivatives. Rejected images are deleted from ignored
working directories and never committed.

For a transparent derivative, read
`skills/aachat-remove-background/SKILL.md` after the RGB master is approved.

The source-asset decision is recorded in
[`docs/asset-audit.md`](docs/asset-audit.md).
