# Rune Types: Three Families

Every stone belongs to one of three families, one per Quiet god (Hush, Mortmain, Grudge). The family is what the man was doing as he died; his strongest verb is the subtype, which is still the root name written as the glyph ([What runes are](what-runes-are.md)). Grudge holds Rend, Break and Sting; Mortmain holds Ward, Still and Sink; Hush holds Hunger and Flee.

## Canon

- **Three major families, one per Quiet god** (round 41, the user's idea). Under each, subtypes.
- **What decides the family** (round 41): the act the man was doing as he died: refusing his death (Grudge), clinging (Mortmain), or slipping away (Hush). It says which Quiet god wants the soul most.
- **Mortmain still holds every forced stone** (rounds 36–37, restated round 41). The family is who is hungriest for the soul, not who holds it.
- **The subtype is his strongest verb at death** (round 41), and the subtype is the root name. A man who refused by cutting gives Rend. Round 3 (type = root name) stands.
- **Folk grades first** (round 41): stones show the gleaners' grades, **biter** (Grudge), **holder** (Mortmain) and **taker** (Hush), until the Wanderer learns the god behind a family; then the label turns to the god's name (like "Echo:" turning into the man's name). Design canon, not built.
- **The mapping** (round 42, built in the Godot build; seen in: godot/scripts/game/rune_book.gd):

| Family (god's act) | Folk grade | Subtypes (where lashed) |
|---|---|---|
| **Grudge: refusing** | biters | Rend (blade), Break (blade), Sting (armour) |
| **Mortmain: clinging** | holders | Ward (armour), Still (blade), Sink (blade) |
| **Hush: slipping away** | takers | Hunger (blade), Flee (armour) |

- **What each subtype does** (round 42, built): Rend sharpens the edge; **Break** fills a break meter toward a knockdown; **Sting** hurts the attacker back; Ward hardens the flesh; **Still** holds struck foes a moment; **Sink** slows them; Hunger drinks from the wounded; **Flee** lengthens the dodge and quickens running.
- **Glyphs** (round 42, built): the family is the glyph's spine, the subtype its marks. No family colour; glow stays tier only (ART_RULES). Fused glyphs: see [Fusing](fusing.md).
- **Fusing across families** (round 42, built): two different subtypes may fuse whatever their families; the stone lashes where either half fits.
- Biomes already match: Ashen Forest favours Rend, Chapel Ruins Ward, Rot Swamp Hunger (seen in: biomes.js).

## Open

- **Fuller favour** (waiting on the user): a stone given to its own family's god gives fuller favour and eases the Pull more; corruption unchanged (it follows the act). Any dark rite still consumes any soul (round 19).
- **Not built yet** (round 42): forced downsides by family; folk-grade labels.

### Loremaster proposals (round 41, not canon)

- Willing stones have a family too (the verb is the soul's own) but no god has a claim on them. Analogy: Mortmain pens all the cattle; the family is which buyer the beast is fattened for.
- Kept as a tendency only: Hush stones often lack their name, Grudge stones the letting go, Mortmain stones the road (the good death mirrored).
- Spine shapes: Grudge one long diagonal cut; Mortmain an upright bar with a short crossbar (a grip); Hush an open hook. Subtype marks 1–3 short strokes (max 6 strokes, ART_RULES §5). (Check against the built icons.)
- Battlefield favours Break, Frozen Pass favours Flee.
- **Resonances:** a family resonance when every stone in one piece shares a family.
- **Forced downsides by family:** biters, the rage turns on you (hurt a little more); holders, the weight (a little slower); takers, the fade (healing reduced).
- **Finds:** a sale-book page with three columns headed by the three spines; reliquaries with three rows of niches; barterer line: "Biters to the blade, holders to the plate. Takers go wherever they'll stay."

## Rejected

- **Family = the rite it was taken under** (round 41): only one trapping rite exists, Mortmain's (round 36).
- **Family = the soul's need** (round 41): the need is learned in layers and changes as it is finished; a glyph can't change.
- **The god's name on screen from the start** (round 41): gives away the dark gods before the story does.

## Related

[Root names](root-names.md) · [What runes are](what-runes-are.md) · [Fusing](fusing.md) · [Willing and forced](willing-and-forced.md) · [Overview of the gods](../Gods/overview.md) · [Offering and favour](../Mechanics/offering-and-favour.md)
