# Canonical local release layout

The canonical local collection point for completed character image packages is:

```text
/Users/takagikensaku/Documents/projects/aachat-characor-release
```

The directory contract is:

```text
aachat-characor-release/
├── README.md
├── level4/
│   └── nouns-classified-1973/
│       ├── README.md
│       ├── manifest.tsv
│       └── B01-HUM__Humanoid/ ... B10-ANO__Anomaly/
└── level5/
    └── README.md
```

`level4/nouns-classified-1973/` is complete with 1,973 native 1254x1254 RGB
PNG masters. Its `manifest.tsv` is the package integrity index.

`level5/` is the reserved collection point for the completed Level 5 package.
Partial worker output, rejected candidates, caches, and production credentials
must not be placed in the canonical release directory.

This local release directory is the source of truth for completed binary
packages while the GitHub storage strategy is being decided. The images are
not added to Git by this document-only change. GitHub publication, production
publication, and runtime cutover remain separate operations requiring explicit
approval.
