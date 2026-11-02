# What Runes Are

A rune is a name written in stone, and every rune holds a trapped soul. Its glow shows how strong the name was (tier); its glyph shows which verb it is (type). Runes are the only vivid color left in a grey world.

## Canon

### Names (round 3)

- **A rune is a name written in stone.** A name is not a label; it is what a thing *does*, given a shape. Carving a name lets it outlast whoever knew it and pass from hand to hand.
- **Root names** are the simplest verbs the world is made of. Each rune type is one root name; its glyph is that name written. (seen in: rune descriptions, runes.js)
  - **Rend:** the name of cutting (an edge, a tooth, a thorn). "Sharpens the edge." Set in the blade.
  - **Ward:** the name of holding (a shield, bark, a shell, stubborn flesh). "Hardens the flesh." Set in armor.
  - **Hunger:** the name of taking from the living (a leech, a crow, rot). "Drinks from the wounded." Set in the blade.
- **Names of kinds** are built from root names (a wolf: Rend and Hunger). Every wolf shares one.
- **True names** belong to noted individuals (bosses, named characters, Hollows of note): their kind's name plus a mark only they have.
- **Every rune holds a trapped soul,** most of them soldiers. (round 3, restated round 7)
- **Design intent:** runes carry fragments of the soldiers in them, so lore can be added to runes as the story goes. (round 3)

### Tiers and look

- **Glow = tier, glyph = type.** (ART_RULES)
- **Tiers** (faintest to cursed): Pale (barely awake), Azure, Violet, Venom, Gold, Crimson. (seen in: rune names, e.g. "Pale Rune of Rend")
- **Tier = how strong the bound name was.** Ordinary soldiers had faint names: Pale. Heroes make Gold. (round 4)
- **The only living thing in a dead world.** Runes glow; nothing else ordinary does. Rune color on a creature means it is rune-touched. (seen in: ART_RULES §1, §3, §7)
- **Form:** a carved fragment of stone, bone, steel or tooth with a glyph cut into it. The base's shape hints at its region. (seen in: ART_RULES §5)
- **Found in:** runestones (Battlefield, Chapel Ruins), reliquaries, corpses, chests, pyres, ice tombs. (seen in: items.js loot tables)
- **Beast stones are findable, rarely, always Pale** (round 34; design canon, not built): left from the testament king's yokes, ploughs and churns. Proposed text: "Ox-stone, from a yoke." Kind names are faint, so beast stones are Pale. A beast stone lends its verb to what it is set in (a yoke, a plough, a churn), like a stone lashed to a blade; it works while set and while its reader lives.
- **Claims:** monk: "The runes remember what we forget." / "Every stone out there was once a promise." (seen in: village.js)

### Lashing (round 39)

- **A stone lends its verb only when lashed against bare steel.** "Lash" / "lashed" replaces "socket" / "socketed" in canon (the code still says sockets).
- **Blade:** three spots, the left guard arm, the right guard arm and the ricasso. **Armour:** two spots, where the straps cross bare plate (Ward).
- **Forced stones are tied with their own wire tail.** Willing stones are bare, so they need cord, gut or thong.
- **No changing stones with Hollows near** (design canon, not built).
- **Open:** whether smithed settings existed as a rich man's fitting (see [The Wanderer](../Characters/the-wanderer.md)).

### Shards, shattering, carving, resonance

- **Shards** "feed a rune's growth" (seen in: Rune Shard description). **Shards are not soul.** (round 8)
- **Shards come only from spoken stones** (round 29). An utterance burns the soul and shatters the empty stone; the pieces are shards. The war uttered thousands, so shards lie wherever it was fought; gleaners gathered them and chapels bought them as carving stock (why reliquaries hold them). **A stone broken unspoken leaves no shards;** it crumbles to dull grit.
- **Shattering** (rounds 8–9, settled round 9 option a):
  - **Spoken:** an uttered rune shatters and its soul is burned to nothing; its hatred raises a Hollow (round 10).
  - **Broken unspoken** (a failed fuse; in the war, stones smashed by the thousand): the soul goes loose, between the afterlife and a body.
  - **The player can't smash a rune on purpose.** (round 10) A failed fuse is the only way he looses souls.
- **Carving** adds notches along the edge, up to five; cracks fill with light as it grows. Each notch strengthens the rune. Costs shards. (seen in: Carve, ART_RULES §5)
- **Resonance:** runes set together in one piece of gear form named effects: Flay, Gorge, Bloodletting, Riposte, Leech-shell (blade); Bulwark, Scab (armor). (seen in: runes.js)

### Related

[Blanks](blanks.md) (how stones are made) · [Origin of runes](origin-of-runes.md) · [Willing and forced](willing-and-forced.md) · [Crimson](crimson.md) · [Fusing](fusing.md) · [Rebuilding and binding](rebuilding-and-binding.md) · [Root names](root-names.md) · [Reading and echoes](../Mechanics/reading-and-echoes.md)

## Open

- **What notches are in-world.** Strokes of the name completed? Undecided.
- **Finite loot:** do runestones and reliquaries ever refill in a saved world? See [Persistence](../Mechanics/persistence.md).
