# aachat character filenames

Status: Current

Updated: 2026-07-25

Each Level adds one segment:

```text
aachat-<stage>[-<group>][-<name>][-<evolution>].png
```

| Level | stage | Required form |
|---|---|---|
| 1 | `seed` | `aachat-seed.png` |
| 2 | `awake` | `aachat-awake.png` |
| 3 | `origin` | `aachat-origin-<group>.png` |
| 4 | `forge` | `aachat-forge-<group>-<name>.png` |
| 5 | `ascend` | `aachat-ascend-<group>-<name>-<evolution>.png` |

Use lowercase ASCII and hyphens only. Never add `level`, a group code, a
sequence number, a size suffix, uppercase, underscores, spaces, or Japanese.

## Groups and folders

| Code | group | Folder |
|---|---|---|
| B01-HUM | `humanoid` | `B01-HUM__Humanoid` |
| B02-FAU | `fauna` | `B02-FAU__Fauna` |
| B03-FLO | `flora` | `B03-FLO__Flora` |
| B04-CUL | `culinary` | `B04-CUL__Culinary` |
| B05-MEC | `machine` | `B05-MEC__Machine` |
| B06-OBJ | `artifact` | `B06-OBJ__Artifact` |
| B07-MAT | `mineral` | `B07-MAT__Mineral` |
| B08-NAT | `nature` | `B08-NAT__Nature` |
| B09-ECH | `echo` | `B09-ECH__Echo` |
| B10-ANO | `anomaly` | `B10-ANO__Anomaly` |

Store Level 4 and Level 5 masters as:

```text
production/forge/<group-folder>/<filename>
production/ascend/<group-folder>/<filename>
```

Ignored candidates and system-approved files use the same relative path below
`.work/candidates/` and `.work/system-approved/`.

## Name and evolution

- Use a meaningful 2–4-word name when practical.
- Decide `<name>` at Level 4.
- Every Level 4 has exactly three Level 5 children.
- Each Level 5 inherits its Level 4 name unchanged and adds one distinct,
  meaningful evolution word.
- Do not use any of the ten group words inside `<name>` or `<evolution>`.
- Do not leave sequence numbers or temporary names in a production master.

Example family:

```text
aachat-forge-flora-moss-beetle-ranger.png
aachat-ascend-flora-moss-beetle-ranger-cathedral.png
aachat-ascend-flora-moss-beetle-ranger-tempest.png
aachat-ascend-flora-moss-beetle-ranger-oracle.png
```

Record parentage in `production/manifest.csv`. A Level 4 parent is its
`aachat-origin-<group>.png`; all three Level 5 rows name the same Level 4
filename.

`production/manifest.csv` contains only:

```text
filename,relative_path,resolution,lineage
```

The approval command adds the row with resolution `1254x1254`. Do not edit a
filename without updating its row.

## Derivatives

Add the purpose at the end. A transparent derivative uses `-alpha`:

```text
aachat-ascend-flora-moss-beetle-ranger-cathedral-alpha.png
```

Keep derivatives outside `production/`; they never replace an RGB master.

## Search

```bash
ls **/aachat-*-flora*.png
ls **/aachat-forge-*.png
ls **/aachat-*-flora-moss-beetle-ranger*.png
```
