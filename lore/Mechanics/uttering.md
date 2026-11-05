# Uttering

Uttering is the only magic: the Wanderer speaks a lashed rune's name through his blade, and the soul inside burns as the spell. The soul is destroyed, Grudge snatches a scrap of its rage, and what's left of its anger gets up as a hatred Hollow.

## Canon (rounds 6–13, 37; built round 48 with the simplifications below)

- **Utterances are the only spells:** speaking a lashed rune's name through the blade. Only lashed runes can be uttered ("socketed" before round 39). It works in combat. The Wanderer stays a melee fighter. (rounds 2, 4)
- **Uttering spends a soul.** The soul leaves the stone only to burn as the spell. It does not reach the good gods; it is burned to nothing. The rune shatters and its shards come back. (rounds 7, 9; burn rule round 10)
- **Uttering spends the name itself.** The name is spoken to cast the spell, so it is used up. That is why a hatred Hollow has no name left. (round 11)
- **What Grudge gets** (round 37; rewords round 13's "no god consumes it, it feeds them only indirectly, never as a meal"): the soul rages as it burns, and Grudge eats the rage as it flares. Only a scrap of a meal. So the dark gods still prefer their own rites, uttering still eases withdrawal less, and the dark monks still want the Wanderer to give, not burn.
- **A hatred Hollow rises nearby.** (round 10) It is what Grudge didn't finish: the kept coal, his smouldering leftovers (round 37). **Its strength scales with the spell's power;** a strong utterance must never raise only a two-hit Hollow. Traits: see [Hollows](../Characters/hollows.md).
- **So every utterance is:** a spell, shards back, the soul burned, corruption up, and a Hollow rises.
- **Spent vs forgotten.** An uttered name is *spent*: the living still remember the word, but it names nothing. An offered name is *forgotten*, even by kin. (round 12)
- **Uttering a Pale rune** crumbles it to dust; it can't be rebuilt. (round 5)
- **At the Pull,** utterances grow stronger and add no corruption. (round 9)
- **Crimson utterances** are their own thing: see [Crimson](../Runes/crimson.md).
- **The Grudge rite is not an utterance** (round 20): no spell, no shards; he gets "Not yet", and a Hollow all the same.

### What the build does (round 48, Godot)

Seen in: godot/scripts/game/utter.gd, RuneBook.SPELLS / UTTER_CORRUPTION / UTTER_SHARDS / HATRED_* in godot/scripts/game/rune_book.gd, hatred Hollows in godot/scripts/hollow.gd.
- **Keys 1–5 speak the stone in each lashing spot:** the blade's three, then the armour's two. Armour stones can be uttered too. Instant, works in combat.
- **One spell per verb,** scaled by tier, notches, fused share and reading:
  - Rend: a burning cut in a cone ahead. Break: knocks down and breaks all near. Sting: splinters all near and makes them bleed.
  - Ward: a health shell on him. Still: holds all near. Sink: drags all near down (slow).
  - Hunger: drinks health from each near foe. Flee: untouchable for a moment.
  - **A fused stone casts both its verbs' spells.**
- **An unread stone works at half power.** No name is needed: what he speaks is the name written in the stone (its verb), not the man's own name, which forced echoes never give anyway. Fits round 11: the name in the stone is what gets spent.
- **The stone is gone from its spot.** Shards come back by tier; a Pale stone gives none and "crumbles to dust" (round 5 and round 29: shards come only from spoken stones, Pale ones excepted).
- **Corruption rises by tier,** less than a dark rite (UTTER_CORRUPTION below DARK_RITE_CORRUPTION; fits round 12's "the offering costs more than an utterance"). **At the Pull** spells are 1.5x and add no corruption.
- **A hatred Hollow rises every time,** climbing out of the ground nearby, stronger by the stone's tier. Traits in [Hollows](../Characters/hollows.md).
- **Crimson can't be uttered yet:** "Not this one. Not yet." *Simplification:* round 30–31's Crimson utterance is canon, not built.
- **The book:** the first utterance writes "utter_first" in his voice (journal.json; a claim, not canon). It also fits "fooled once" for Grudge (round 20): the first hatred Hollow is how he meets Grudge's work.
- *Not built:* Grudge's scrap (uttering easing withdrawal at the Pull); villagers remembering an utterance.

## Open

- **Uttering inside village walls** (partly settled by the build, round 48): allowed, and the hatred Hollow rises inside too. But the Hollow barrier stops Hollows chasing a man inside a village (hollow.gd player_safe), so the Hollow wanders and can be cut down for free: a safe place to utter. Still open: should hatred Hollows ignore the barrier (fits the guard's "Keep your blade low inside the walls."), or rise past the wall like the Grudge rite's ("Past the wall, something gets up.")? Villagers remembering it stays a proposal.
- **Built vs canon, round 48 flags:**
  - **"Through the blade"** vs armour stones being uttered. Proposal: reword to "through the steel it's lashed to" (round 39 lashes armour stones to bare plate).
  - **A fused stone holds two souls, but one Hollow rises.** Canon says every burned soul raises one. Proposal: two Hollows, each at its own half's tier; or one Hollow at the higher tier with both souls' ember ("two men's anger in one body").
  - **Strength by tier, not by spell power.** Round 10 ties the Hollow to the spell; the build ties it to tier, so a half-power unread utterance raises a full-tier Hollow. Proposal: accept it and reword to "scales with the soul's tier": the hatred is the soul's, not the spell's.
  - **"Not this one. Not yet."** on Crimson echoes Grudge's favour "Not yet". Fits: Grudge won't let the Unfallen go. Keep it deliberate.
- **Proposal (round 37, not recommended):** uttering a willing rune raises no Hollow. Breaks "every utterance raises a Hollow".

## Rejected

- **Uttering frees the soldier** (rounds 3–4). Replaced round 7.
- **"Not in combat" meaning no utterances in combat.** Rejected round 4.
- **Uttering looses the soul to wander forever** (round 8 option b). Rejected round 9.
- **Every utterance is a small offering to the dark gods** (round 8 fix 2). Rejected round 9: only an offering is Hush's meal. (Round 37 makes uttering a scrap for Grudge, not an offering.)
- **Every utterance looses the soul into a body scaled to the spell** (round 10 option 2). Rejected round 10: the soul is burned; the Hollow comes from its hatred.
- **Smashing a rune as a player action** (round 9). Rejected round 10: it gives the player nothing.
