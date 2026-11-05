# The Six Rites and Souls' Needs

Each of the six gods has a rite, and the Wanderer gives a soul to one of them. To free a soul he must find out which parts of the good death it missed and finish them in order, ending at Wend's road. The dark rites never look evil; they look like the kind, easy option.

## Canon (rounds 19–21; design canon, not built)

### The rites

- **Every god has a rite; the Wanderer gives a soul to one.** (round 19)
- **The three dark rites all consume the soul, each its own way:**
  - **Mortmain locks it up** ("Lay him in the niche"). Binding only ever answers "the name is held"; kin still remember; never freed.
  - **Hush eats the name** (the offering; "Scrape his name"). Forgotten even by kin: the Greying.
  - **Grudge twists the soul into a Hollow** ("Bank the coal"). Favour: "Not yet".
  - All three ease withdrawal at the Pull; uttering eases it less.
  - **Every dark rite costs corruption,** Mortmain's and Grudge's as much as Hush's. (round 20; amount is tuning, the offering is the reference)
- **Only Wend's rite (the Walking) lowers corruption.** (round 20)
- **Ennick's and Gled's rites finish a part of the death;** the soul goes free only at Wend's road. No corruption drop. Their small buffs (round 21) stay practical, never combat power. (See [Ennick](../Gods/ennick.md), [Gled](../Gods/gled.md).)

### The places and the words (round 19, kept round 20)

The dark rite is offered at the same place as its good twin:
- **The ledger** (Chapel Ruins; every village since round 47): Ennick "Write his name" / Hush "Scrape his name".
- **The fire:** Gled "Give him to the fire" / Grudge "Bank the coal".
- **The road shrine** (wayside shrines; every village since round 47): Wend "Leave him by the road" / Mortmain "Lay him in the niche" (an iron grate closes; the stone stays visible forever).

**The place is not the moral switch.** What decides is what the soul needs. (round 20)

**Every village holds all three places** (round 47, decided by the user): its own ledger, its firepit as the fire, and a road shrine just inside the south gate beside the path. The chapel ledgers ([Chapel Ruins](../Locations/chapel-ruins.md)) and the [wayside shrines](../Locations/wayside-shrines.md) on the old roads still exist and still work; villages are simply the places where all three stand together. The wild ones keep what villages lack: chapel ledgers hold the war's names (rite cords, Crimson name pieces), and wayside shrines hold the Crimson Release and the old roads' milestones. (seen in: godot/scripts/world/villages.gd, godot/scripts/game/rites.gd, godot/scripts/ui/rite_panel.gd)

**The Wanderer may perform the rites at any village's ledger, fire and road shrine because he is an ordained chaplain** (round 48, decided by the user: "Since the stranger is a monk (chaplain to be exact) he can."). Settles round 47's flag against round 38b. Round 38b still holds for the *last rite* over a village's own dying: families pick their own monk over a stranger (seen in: journal.json "talk_first", "They would not have a stranger, and they are right."). Supporting colour only: a stone is no one's dead in the village, so no family asks to choose.

**The game never names the god behind a rite** (round 48, design rule from the user). The rite panel shows only each rite's words ("Write his name", "Bank the coal"…), and the book's rite entries don't name Ennick or Gled. The player isn't told which god a rite belongs to; he works it out. (seen in: godot/scripts/ui/rite_panel.gd, godot/scripts/game/journal.json "rite_*"; the god stays an internal key in rites.gd) Knock-ons are listed under Open.

### What the build does (round 47, Godot)

Built from the canon above; simplifications marked.
- **Common souls draw one need from their soul id:** nameless (Ennick, then Wend), unforgiven (Gled, then Wend) or ready (Wend only). *Simplification:* "kept by kin" not built.
- **The need shows only once the stone is read; good rites refuse an unread stone:** "You don't know him yet. Read the stone first." This settles "why doesn't everyone free runes at shrines?" the proposed way: a stone must be read first.
- **Wend with needs unfinished:** "He would not go." The stone stays with him, so he can take it back after (settles that proposal). The nameless case uses the same line, not the proposed "No one called him."
- **Ennick** writes a generated name into his book's roll of names ("Written: %s."). *Simplification:* Gled needs no keepsake item for common souls yet.
- **Dark rites** destroy the stone and add corruption by tier; **Wend's** lowers it by tier. Hush: "The name goes out of the ledger." Mortmain: "The grate shuts. He stays." Grudge: "The coal takes him. Past the wall, something gets up." (no Hollow spawns inside the walls).
- **In the Whisper** Mortmain's words read "Keep him safe".
- **At the Pull** a good rite is said kneeling and costs health ("Kneel. It costs blood."). *Simplification:* the kneel (round 20, [Corruption](corruption.md)) is a flat health cost, with no held button or dimming. (seen in: rites.gd kneels, RuneBook.KNEEL_BLOOD)
- *Not built:* Crimson stones get no rite ("No rite reaches a Crimson stone."), though round 31's Release is canon; favour and Pull-easing from dark rites; "fooled once" (learning each dark rite).

### Each soul needs something (round 20)

- **Every trapped soul missed the release; many also missed other parts.** Freeing means finding what it lacks and finishing those parts **in order, ending at Wend's road.**
- **The needs:**
  - **Its name** (cord lost, ledger page torn). Good: Ennick; find the name through kin, ledgers or cords and write it. Tempting dark: Hush, "Let him rest unnamed."
  - **Letting go** (died angry, ashamed or unforgiven). Good: Gled; find what it holds onto (a keepsake, a letter, the man it hated) and burn it. Tempting dark: Grudge; give it the fire it wants, and its anger becomes a Hollow.
  - **Someone to let it go** (kin can't let go). Good: Gled, with the kin: they burn their keepsake themselves (a quest with a living person). Tempting dark: Mortmain, "Keep him close to her"; the stone goes behind the grate where she can visit.
  - **Just the road** (named and at peace). Good: Wend. No dark temptation.
- **The dark rites look like giving the soul what it asks for.** He favours the dark gods by being kind in the cheap way.
- **A wrong rite:** a soul left at the road that still holds something stays. Next visit: "He would not go." No punishment beyond the walk.
- **Common souls have one need plus the release; notable souls can stack needs.** (round 21)

### Learning what a soul needs: four layers (round 20)

1. **The echo** from reading the rune: "Tell her I'm sorry." / "Who was I." / "Don't let them see what I did."
2. **The rune's details:** tier and company hint at the story.
3. **The world:** kin in villages, ledgers in the Chapel Ruins, cords on bodies.
4. **The dark monk shortcut:** he always points to the dark rite ("This one wants to forget. I can help."). A lie of omission.

### Procedural and authored souls (round 20)

- **Common runes** draw one need from a small set (nameless, unforgiven, kept by kin, ready), with templated echoes and a generated kin villager nearby. The need is game state; the dialogue model may phrase it later.
- **Notable runes** (Gold, willing, story) get authored stories.

### Fooled once (round 20)

He learns each dark rite by being fooled into it once, as he was fooled as a chaplain. After that it stays known.
- **Hush:** a dark monk offers to "ease" an ashamed soul; the name vanishes from the ledger, and later the kin can't remember it.
- **Mortmain:** a grieving villager asks him to "keep" her son; the niche is the kind option; binding later answers "the name is held".
- **Grudge:** the first hatred Hollow rises from an utterance; the ember is recognised later at a fire.

## Open

- **Why doesn't everyone free runes at shrines?** (round 16 hole 4) The build settles the first half (a stone must be read first, round 47). Still proposal: peasants can't read stones, so no one else can.
- **No god names in the game: knock-ons** (round 48 flags). (a) Round 41 says a stone's folk grade "turns to the god's name" once learned; under the new rule it would never turn. (b) The book's death entries still name Wend ("Wend walks the dead home.", "Wend has little left to spend"). (c) The villager dialogue data names the gods often (dialogue/data/lore/monk.jsonl and others). (d) A chaplain knows the three good gods by name, so his silence about them needs a reason; he doesn't know the Quiet gods at the start, so silence about them is natural. Proposal for (d): the Order teaches brothers never to say a god's name over the dead ("Say the work, not the name"), because a name spoken is a name spent; it is also why the Quiet gods could hide inside the same words.
- **Dark rites without the dark monk:** round 19 has a known dark monk perform them for metal, and "fooled once" gates each. In a village the Wanderer can do them himself; if the build offers them from the start, that skips "fooled once". Proposal: the dark words stay greyed in the panel until learned.
- Binding a Grudge-twisted soul: see [Grudge](../Gods/grudge.md). Hush's place clash: see [Offering and favour](offering-and-favour.md).

## Rejected

- **The place as the moral switch** (three places, two rites each, pick good or dark; round 19). Replaced round 20 by the needs model: it made the favoured god obvious and forced the player's hand. The places and words are kept.
