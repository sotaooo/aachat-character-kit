# Concept workflow

## Good concept shape

Store the concept itself as one short, natural sentence. Keep strong user
wording instead of replacing it with an analytical abstraction.

Examples:

- 高級車のデザインをした、光沢があるもの
- 1980年代のアメリカ西海岸をモチーフにしたファッションをしている
- 電化製品をモチーフにした、光沢があって高級感があるもの
- タバコの箱の銘柄たちをモチーフにしたもの
- ヨーロッパの有名な建築物をモチーフにしたデザイン
- エジプトを想起するようなデザインモチーフ
- 『バック・トゥ・ザ・フューチャー』の世界観をモチーフにしたもの
- カクテルの種類ごとの色・器・味の印象をモチーフにしたもの

Add `design_cues_ja` to describe usable visual evidence: palette families,
surface finishes, textures, silhouette tendencies, clothing construction,
spatial relationships, and characteristic motion. The production agent—not the
catalog—decides the final body, role, and detailed prompt.

## Mass concept generation

1. Collect visually rich themes from products, fashion, packaging,
   architecture, civilizations, fiction, manga, games, luxury goods, food,
   places, cultures, craft, science, nature, and abstract systems.
2. Write each as a direct concept sentence that can be handed unchanged to the
   production agent.
3. Keep only themes broad enough to yield 20 different attempts.
4. Let the production agent invent the role, body architecture, mechanism,
   silhouette, and prompt after selection.

Reject a source concept when:

- it is an incoherent random combination;
- it is only a parts list;
- it is so narrow that 20 attempts would become recolors;
- it is so empty that the agent must invent the real concept;
- it is likely to produce a literal logo, package, food, or landmark with limbs
  rather than a designed character;
- it depends on stereotyping a culture, ethnicity, or religion.

Vary design domains:

- luxury product and mobility;
- era/place fashion;
- packaging and graphic culture;
- architecture and civilization;
- craft and material culture;
- performing arts and ceremony;
- civic functions and public services;
- food process rather than food costumes;
- weather, geology, optics, and environmental systems;
- information, memory, causality, and spatial contradictions.

## Named works, characters, products, and brands

Use names only as private research provenance in `reference_note_ja`. Never put
them in `concept_ja`, `design_cues_ja`, `production_instruction_ja`, or the image
prompt. List title, franchise, brand, and character-name variants in
`blocked_terms`; catalog validation fails if any blocked term appears in a
production field. `prepare_batch.py` removes both private fields.

Translate a reference into concrete, name-free evidence. Cover as many of these
as apply:

- head and body proportions;
- dominant silhouette and negative space;
- two or more palette families;
- material and finish hierarchy;
- garment cut, layering, closures, and footwear;
- signature mechanism or transformation;
- movement and stance;
- at least three spatial relationships between major parts.

Do not write “a famous sci-fi hero” or “a premium brand style.” Write what can
actually be drawn. Reject the entry if the description still depends on knowing
the hidden name.

Do not create one concept per individual brand, model, package, or character
when the item cannot support 20 substantially different attempts. Consolidate
it into a product family, fictional-world grammar, power-system family, or
creature-design family.

## Nations, regions, ethnic traditions, and religion

- Prefer specific climate, architecture, craft process, material, music, food system, procession, or public ritual over generalized ethnicity.
- Do not turn sacred figures, scripture, ritual garments, or protected ceremonial objects into costumes.
- Do not invent readable sacred text.
- Avoid exoticism, caricature, skin-tone coding, and mixing unrelated cultures.
- State a `cultural_note` when a concept requires extra care.
- If accurate treatment would require research not present in the repository, keep the concept at a broad architectural/material level or pause for research.

## B09 Secret Echo

Start with one operation on information or memory:

- missing;
- repeating;
- delayed;
- overwritten;
- misremembered;
- recorded before it happens.

Convert that operation into silhouette, layers, negative space, material behavior, or motion. Keep the LCD perfectly stable. Avoid brain, heart, speech-bubble, and generic ghost symbols.

## B10 Secret Anomaly

Start with one renderable impossible physical law:

- center of gravity outside the body;
- inside and outside exchange places;
- effect appears before cause;
- discontinuous volume;
- incompatible scales coexist;
- one surface has two spatial orientations.

Make every form obey that single law. Keep the LCD perfectly stable. Avoid random distortion, horns, wings, black-and-gold armor, and horror costumes.

## Catalog record

Required JSONL keys:

```json
{
  "concept_id": "CONCEPT-001",
  "concept_ja": "高級車のデザインをした、光沢があるもの",
  "design_cues_ja": "長い流線形、厚い曲面、深い鏡面塗装…",
  "suitable_origins": ["B05-MEC", "B06-OBJ"],
  "levels": [4, 5],
  "difficulty": "standard",
  "source_domain": "luxury-products"
}
```

Optional provenance keys:

```json
{
  "reference_note_ja": "Research provenance only; never sent to generation.",
  "blocked_terms": ["work title", "franchise", "brand", "character name"],
  "cultural_note": "Avoid sacred or identity-defining costume elements."
}
```
