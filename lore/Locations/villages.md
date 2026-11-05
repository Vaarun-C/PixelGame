# Villages

Rare walled villages: each one an organic shape walled by a ragged palisade, with a well, a barter stall and all three rite places inside: a ledger, the firepit and a road shrine by the south gate. The game starts in one after its prologue, and the Wanderer wakes in one after death. The people there are listed in [Villagers](../Characters/villagers.md).

## Canon

- **Rare. Organic, not square (round 43, decided by the user): each village has its own lobed outline, walled by a ragged palisade that follows it, with a gate roughly north and south (either can sit off-centre). Torch posts beside the gates and here and there along the wall. Inside: a well, a barter stall, a firepit, and a random number of buildings, more in bigger villages, packed close.** (seen in: godot/scripts/world/villages.gd)
- **Every village holds all the ways of performing the rites** (round 47, decided by the user): its own **ledger** (Ennick "Write his name" / Hush "Scrape his name"), its **fire**, the firepit (Gled "Give him to the fire" / Grudge "Bank the coal"), and a **road shrine** just inside the south gate beside the path (Wend "Leave him by the road" / Mortmain "Lay him in the niche"; the iron grate stays shut after). The ledger and firepit sit near the well. See [The six rites](../Mechanics/the-six-rites.md). (seen in: godot/scripts/world/villages.gd LEDGER_SLOTS, shrine_slots; godot/scripts/game/rites.gd; godot/scripts/ui/rite_panel.gd)
- **Grudge's rite at the village fire raises its Hollow outside the walls, not inside:** "The coal takes him. Past the wall, something gets up." (round 47, built behaviour; seen in: rites.gd) Why it rises there is open, see [Grudge](../Gods/grudge.md).
- **Buildings are mixed and bigger than before: sheds, cottages, barns and a longhouse, with crates among them.** (round 43, decided by the user; design canon: the Godot build has only huts today, see villages.gd BUILDINGS)
- **Villagers: 2–6 besides the barterer, at least one peasant, at most one monk, each starting near a house door.** (round 43, decided by the user; seen in: villages.gd PEOPLE)
- **Names like Greywell, Ashbarrow, Cinderford, Ravengate.** (marked "seen in: village.js", but not in the code today; round 32 note)
- **People:** peasants, monks, guards, one barterer per village. The monk is the carver who rebuilds runes for metal. (carver: design canon)
- **The only place a shattered rune can be rebuilt.** (design canon)
- **Persist once generated, with the same people.** (round 8)
- **Where a new game starts and where the Wanderer comes back after death.** (round 9; partly built) Round 38: a playable prologue at the war's end comes first; the game then cuts to year 0 in a village.
- **Claims:** peasant: "Don't drink from the well after dark." Guard: "Walls won't hold forever. Neither will I." / "Keep your blade low inside the walls." / "Seen worse than you come through that gate."
- **Villages keep their own monks for the last rite** (round 38b): those monks gave the rites to their ancestors, so villagers would rather have them than a stranger. Why the Wanderer gets no dying to shrive in play. See [The Wanderer](../Characters/the-wanderer.md).
- **The Wanderer may still use any village's ledger, fire and road shrine for the rites, because he is an ordained chaplain** (round 48, decided by the user; settles the round 47 flag). The village monks keep the last rite for their own dying; the rite places are open to any brother. A stone is no one's dead here, so no family asks to choose (supporting colour, not the reason).
- **The dead are burned, not buried; there are no headstones** (round 39; settles round 14's "villages burn their dead" proposal). Fits Gled: burned bodies do not walk. **Flagged:** the Frozen Pass's cairns and ice tombs (in game, biomes.js) and "the sacrifice's grave" in [Crimson](../Runes/crimson.md) need a reason or a reword.
- **Every village holds a chapel, where the village monk lives and sells true blanks** (round 49b, the user; design canon, not built). See [Rebuilding and binding](../Runes/rebuilding-and-binding.md).
- **No common standard:** each walls itself in and sets its own barter rates (R3, round 22).

## Open

- **The chapel's knock-ons** (open questions, round 49b): (a) a chapel in every village vs round 43's "at most one monk" and its building list: does a monkless village have a chapel no one lives in? [Every village has its monk now; or an empty chapel whose stock the eldest keeps.] (b) Where does the ledger sit? [Inside the chapel.] (c) Who makes the blanks he sells: see [Rebuilding and binding](../Runes/rebuilding-and-binding.md) Open.

- **Line proposal for the village monk** (left from the round 47 proposal, which round 48 settled the user's way): "The fire is for anyone's dead. That stone is not mine to say over." Fits "A shriving hand holds no stone": the monk won't touch it, the chaplain will.
- **Uttering inside the walls, partly settled by the build (round 48):** allowed, and the hatred Hollow rises inside too, but the Hollow barrier stops Hollows chasing a man inside a village, so the Hollow wanders harmless and can be cut down for free. See [Uttering](../Mechanics/uttering.md) Open.
- **Who keeps the ledger where there is no monk** (at most one per village). Proposal: the eldest peasant, who can't read the names, only count the lines.
- **What a village ledger holds.** Proposal: the village's own dead, burned at its fire, with their cord knots. No pieces of Crimson names (those stay in chapel ledgers). It is also a list of names, which keepers want for binding.
- **Mortmain's grates fill up.** Every niche rite leaves a shut grate by the gate path, and villagers walk past it. Proposal: they read a shut grate as "kept close", a comfort, which is the lie working.
- **The well after dark.** What is in the water?
- **When villages walled themselves in;** proposal: each counts winters since its gate shut (see [The land](the-land.md)).
- **Line proposals for burning** (round 14): peasant: "We burn ours. Others weren't so lucky." See [Villagers](../Characters/villagers.md).

## Rejected

- **Square log stockades with a gate north and south, torch posts at corners and gates, inside a well, a barter stall, a firepit, huts and crates.** Rejected in round 43 by the user: "I don't want it to be a box." Villages are organic shapes with a random number of houses and villagers. The well, stall, firepit and the north and south gates stay. (seen in: the old village.js)
