# aachat Character Kit

A small, agent-neutral kit for making aachat evolution sets: one Level 4 and
exactly three Level 5 children.
Codex, aachat, or another image-capable agent can use the same four references,
one specification, and one approval flow.

## Start

1. Read [`SKILL.md`](SKILL.md).
2. To use the helper scripts, use Python 3 and install their small dependency:
   `python3 -m pip install -r requirements.txt`.
3. Build a prompt:

   ```bash
   python3 scripts/build_prompt.py \
     --mode concept --level 4 \
     --brief "A monsoon observatory carried as a living instrument"
   ```

   Optional examples and LCD correction wording are in
   [`references/PROMPT_GUIDE.md`](references/PROMPT_GUIDE.md).

4. Read [`references/NAMING.md`](references/NAMING.md), then generate Level 4
   followed by three distinct Level 5 evolutions at the regulated paths under
   `.work/candidates/`.
5. Record a system pass only after mechanical and visual QA:

   ```bash
   python3 scripts/kit.py system-pass \
     .work/candidates/forge/B08-NAT__Nature/aachat-forge-nature-monsoon-observatory.png \
     --visual-pass
   ```

6. Show the four system-approved images together. Only after explicit human
   approval:

   ```bash
   python3 scripts/kit.py approve \
     .work/system-approved/forge/B08-NAT__Nature/aachat-forge-nature-monsoon-observatory.png \
     --lineage aachat-origin-nature.png --human-approved
   ```

   Approve Level 4 first, then its three Level 5 children. Run `family-check`
   on the production Level 4 to confirm the 1+3 set.

`production/` contains human-approved opaque RGB masters and their minimal
lineage manifest. `derivatives/transparent/` contains optional RGBA
derivatives. Unreviewed and rejected images are never committed.

For a transparent derivative, read
`skills/aachat-remove-background/SKILL.md` after the RGB master is approved.

The source-asset decision is recorded in
[`docs/asset-audit.md`](docs/asset-audit.md).
