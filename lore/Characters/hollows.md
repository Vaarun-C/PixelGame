# Hollows and Other Creatures

Hollows are the walking dead: bodies whose souls went into stones. Most are walked by loose souls from stones broken in the war; killing one only lays it down until the soul finds another corpse. Others are hatred Hollows, Grudge's leftovers from an uttered rune, which burn in ember and stay dead.

![A Hollow](../images/hollow.png)

## Canon

- **Monsters were once human or animal.** (seen in: ART_RULES §7)
- **Hollows:** husks of dead soldiers. Slow; they lunge with a spear thrust, telegraphed by the body flashing ember and the thrust's wind-up (no warning on the ground). A slain Hollow leaves its body, which can be searched. (seen in: enemies.js, body prop)
- **Their souls went into the stones,** first under the false rites, then harvested in the war. That makes them hollow. (rounds 2–4, 7)

### Two kinds (round 10)

- **Loose-soul Hollows:** a loose soul from a stone broken unspoken (in the war, or a failed fuse) walks a dead body. Most Hollows on the old fields. They look as they do now (enemies.js). Also: a cut-short rite with no blank leaves the soul loose (round 36).
- **Hatred Hollows:** a soul burned by an utterance raises one nearby; strength scales with the spell. It is what Grudge didn't finish eating: the kept coal (round 37). Traits (round 13):
  - **No name left** (the utterance spent it); nothing to bind; only fought. (rounds 11, 13)
  - **Once killed, it stays dead.**
  - **Rises burning at the seams in ember,** never tier color, so it isn't rune-touched and drops no rune.
  - **No searchable body** (proposed: "Nothing but ash.").
  - **Strength set by which corpse the hatred seizes:** a Pale utterance stirs a peasant's bones, a Gold one drags a knight from the mud.

### Loose souls (rounds 8–10, 13, 15)

- **Souls from runes broken without being spoken,** adrift between the afterlife and a body. **They fill most Hollows.** Uttered souls are burned and never loose.
- **Killing a loose-soul Hollow only lays it down** (round 15, B1 + B4):
  - A loose soul takes the **nearest unburned corpse.**
  - After a lull (an area reload or a night) it walks again **in a corpse that hasn't risen yet.** Only binding ends a loose soul's walking.
  - **Killing a Hollow adds no corruption.**
  - **A risen corpse carries only what it still had.** A searched body rises empty.
  - **A Hollow takes the Wanderer's dropped bag** if he dies again before reaching it (round 24); hatred Hollows never do.
  - **Burned bodies do not walk.**
  - **Loose animal souls walk animal corpses** (round 34): a beast stone broken unspoken looses a beast soul.
- **A soldier's soul is freed only when his rune is given back to a good god;** uttering it destroys him. (round 7)
- **Binding calls a name, not a body** (round 13); results: see [Rebuilding and binding](../Runes/rebuilding-and-binding.md).
- **Names come from kin,** and rarely from a **rite cord** tied at the dying man's wrist (round 19); its knots are a number looked up in a chapel ledger or with a monk.
- **Dark monks lie about rite cords by swapping** (round 15, C1): asked to read a cord, a dark monk gives another real dead man's ledger name and keeps the true one. Scripted, from game state.
  - **Found out** by reading the bound rune (wrong man) and checking the cord in a Chapel Ruins ledger.
  - **He lies to the clean and stops lying near madness.**
  - **The swapped name can be a living villager's** (C2, round 21; see [The living binding](../Mechanics/the-living-binding.md)).
- **Clue names never lie, even during the Whisper** (round 15): ledger lines, cord readings and binding names are exact game strings. (A dark monk's swap is a character's lie.) Narrowed round 20: names only; echoes can be misheard.

### Others

- **Rune-corrupted creatures** show their rune's tier color in eyes, veins or an embedded rune, and drop a rune of that tier. (ART_RULES §7; not in game yet)
- **The Unfallen,** the Crimson prisoners: see [The Unfallen](the-unfallen.md).

## Open

- **Can a man's loose soul take a beast's body, or the reverse?** Proposal: no; "nearest unburned corpse" means nearest of its kind.
- **Corpse budget under persistence:** each kill uses up a corpse for good, so an area's Hollows thin out; a loose soul with no corpse left drifts unseen until bound. Proposal: accept it.
- **Ten years in the open leaves bones, not husks** (round 32 note). Proposal: a body walked by a loose soul doesn't rot fully (it is held); unwalked dead go to bone.
- **Grudge-rite Hollows:** see [Grudge](../Gods/grudge.md).

## Rejected

- **Hollows lost their names only to become a kind** (round 2 option 1) and **every Hollow keeps a name too faded to read** (option 3). Rejected round 3: the names went into the stones.
- **Loose-soul options rejected round 15:** **B2** a body like its own (soldier to soldier; extra rule for little gain); **B3** killing ends it (makes binding pointless, empties fields too fast); **B1 alone** killing looses the soul again at once (endless respawn).
- **Dark monk lie options rejected round 15:** **C3** ordinary monks misread rotted cords too (muddies the clue); **C4** dark monks never lie, only withhold (too weak a tell).
