---
name: aachat-character-kit
description: Generate, revise, QA, approve, and derive transparent copies of aachat evolution sets containing one Level 4 and exactly three Level 5 children. Use for concept generation without an external character reference, reinterpretation with a supplied reference image, Level 4 to Level 5 branching, regulated filenames and lineage, exact aachat LCD construction, production-master validation, human approval, rejection, or transparent RGBA derivative review.
---

# aachat Character Kit

Use one short path from request to approved master. Keep generation-tool choices
outside this kit so Codex, aachat, and other agents can follow it unchanged.

## Read first

Always read `references/SPEC.md` for design and image requirements and
`references/NAMING.md` for filenames, group folders, and lineage. Do not invent
additional fixed ratios, schemas, profiles, or calibration sets.

## Choose exactly one input mode

- **Concept mode:** no character-specific design image was supplied. Write one
  concrete visual brief from the human request. When the human requests ideas
  or has not chosen a direction, select or adapt an entry from
  `assets/concepts.jsonl`; follow `references/CONCEPTS.md` when expanding the
  catalog or translating an entry into visual design cues.
- **Reference mode:** an external source image was supplied. Inspect it and
  write a short brief of its silhouette, palette, materials, construction, and
  prop relationship. Replace its face with the aachat LCD; never paste an LCD
  over the old face.

Keep the same mode for the evolution set. In reference mode, preserve recognizable
design language while removing logos, readable text, protected character
identity, watermarks, and source-image artifacts.

## Select references

Attach only what the image generator needs:

- Level 4 concept: LCD face master and Level 4 anchor.
- Level 4 reference: supplied source, LCD face master, and Level 4 anchor.
- Each Level 5 concept: system-approved Level 4, LCD face master, and Level 5
  anchor.
- Each Level 5 reference: supplied source, system-approved Level 4, LCD face
  master, and Level 5 anchor.
- Add `references/aachat-master-spec.png` only when the tool accepts another
  reference or an LCD/composition failure needs correction.

The anchors control construction quality, not the new character's design.

## Build and run

Always create one Level 4 and exactly three Level 5 children. Generate and
inspect Level 4 first, then use that exact image as the common evolution source.
Give the three children distinct transformation theses; do not make color
variants.

Build the Level 4 prompt:

```bash
python3 scripts/build_prompt.py \
  --mode concept \
  --level 4 \
  --brief "A monsoon observatory carried as a living instrument"
```

Replace the mode and brief to match the human request.

After Level 4 passes system QA, run this separately for each of three Level 5
directions, using the same mode and original brief:

```bash
python3 scripts/build_prompt.py \
  --mode concept \
  --level 5 \
  --brief "A monsoon observatory carried as a living instrument" \
  --lineage "<two retained Level 4 anchors>" \
  --transformation "<at least three transformed axes>"
```

The generated prompt is a starting point, not locked wording. When a stronger
prompt or LCD correction is useful, optionally read
`references/PROMPT_GUIDE.md` and adapt its examples to the human request.

Choose the group, Level 4 name, and three evolution words using
`references/NAMING.md`. If needed, create the two ignored stage/group folders.
Generate each native 1254×1254 result directly at its regulated candidate path.
Inspect the actual image after every attempt. Revise the brief or prompt to fix
the observed failure; do not repair a wrong-sized result by resizing, padding,
format conversion, or relabeling.

## Gate and approve

1. Inspect the image against `references/SPEC.md`. Optionally use
   `references/REVIEW_CHECKLIST.md` as a reminder; it requires no score or
   written QA record.
2. If any item fails, run `python3 scripts/kit.py reject <candidate>` or revise
   with a new attempt. The reject command only deletes files under `.work/`.
3. If all visual items pass, run:

   ```bash
   python3 scripts/kit.py system-pass <candidate> --visual-pass
   ```

   This verifies the mechanical contract and moves the file to ignored
   `.work/system-approved/`. A system pass is not human approval.
4. After Level 4 and all three Level 5 children pass, show the four exact files
   together to a human. Do not infer approval from silence.
5. Only after explicit approval, run:

   ```bash
   python3 scripts/kit.py approve <system-approved-file> \
     --lineage <parent-filename.png> --human-approved
   ```

   Approve Level 4 before its three Level 5 children. This preserves the
   stage/group path, moves each RGB master into `production/`, and adds its
   lineage to `production/manifest.csv`. If a child is rejected, replace it
   until exactly three are human-approved. Never approve directly from
   `.work/candidates/`.
6. Confirm the finished family:

   ```bash
   python3 scripts/kit.py family-check <production-level-4-file>
   ```

## Transparent derivatives

When a transparent copy is requested, read and follow
`skills/aachat-remove-background/SKILL.md`. It creates an ignored candidate,
checks it at native resolution, and moves only a visually accepted derivative
into `derivatives/transparent/`. Never replace the RGB master.
