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
- **The ledger** (Chapel Ruins): Ennick "Write his name" / Hush "Scrape his name".
- **The fire:** Gled "Give him to the fire" / Grudge "Bank the coal".
- **The road shrine:** Wend "Leave him by the road" / Mortmain "Lay him in the niche" (an iron grate closes; the stone stays visible forever).

**The place is not the moral switch.** What decides is what the soul needs. (round 20)

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

- **Wrong-rite edge cases:** an unnamed soul left at the road (proposal: it stays, "No one called him."); can he take a stone back after "He would not go"? (proposal: yes).
- **Why doesn't everyone free runes at shrines?** (round 16 hole 4) Proposal: freeing needs the name, so a stone must be read first; peasants can't read stones.
- Binding a Grudge-twisted soul: see [Grudge](../Gods/grudge.md). Hush's place clash: see [Offering and favour](offering-and-favour.md).

## Rejected

- **The place as the moral switch** (three places, two rites each, pick good or dark; round 19). Replaced round 20 by the needs model: it made the favoured god obvious and forced the player's hand. The places and words are kept.
