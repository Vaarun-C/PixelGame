# Lore

The canon for the world and story, split by subject. Each file starts with a short plain summary, then **Canon**, **Open** (not canon) and **Rejected** (with reasons). The round-by-round record is in [log.md](log.md).

## Conventions

- **Canon:** decided by the user or established by the game.
- **Design canon:** decided by the user but not built yet.
- **Proposal / Open:** floated, not decided. Never canon.
- **Claim:** something a villager *says*; not proven truth.
- **"seen in":** where a fact shows up in the game (a file, sprite or text).
- **(round N):** the round it was decided, so every decision stays traceable.
- **Withheld:** answers kept back on purpose; listed in each file's Open section.

## Ground rules

- **Scope:** single-player for now. Online may come later, so lore shouldn't make it impossible. (round 4)
- **World persistence** (round 8, design canon, not built): the world is generated procedurally but every generated area is saved, Minecraft-style. Going back loads it as it was, so villages, villagers and monks persist and each can remember the Wanderer. (Today a new seed rolls every load; only the inventory persists. See world.js, village.js.) Open questions: [Persistence](Mechanics/persistence.md).
- **Start and death in a village** (round 9, design canon): a new game opens with a playable prologue at the war's end (the Wanderer at the Pull reads the Rend stone, round 38), then cuts to year 0 in a village; after death the Wanderer comes back in one. (Partly built: main.js respawns at the last village entered, south side; the bag and lashed stones are kept. Death costs: [Death](Mechanics/death.md).)
- **Villager dialogue from a small language model** (round 9, design idea, not lore canon): trained on English and this lore; each villager holds only a prompt template, with guardrails. The engineering isn't judged here.
- **Dialogue lore rules** (round 10; apply to every villager template):
  - **Allegiance stays out of the model.** A dark monk's prompt holds only his cover and his tells; whom he serves lives in game state, and every reveal is a scripted line or event.
  - **Whitelist, not invention.** Each villager answers only from a fixed list of what they know. Anything else, and every withheld answer, is "I don't know" in their voice.
  - **Clues are exact strings.** Prisoner true names, ledger entries and names of the dead used for binding are inserted by the game, never generated.
  - **Tone guard.** Short, grim, plain words; never cheerful, modern or heroic.
  - Each template holds: role and village; mood and what they lost; what they know; cover line and tells; the dead they can name (exact strings); banned topics and withheld answers; speech style; what they remember of the Wanderer.
- **No god names in the game** (round 48, the user): the rite panel shows only each rite's words, and the book doesn't name the gods behind them. The player isn't told which god a rite belongs to. God names stay in lore and code keys. Scope open (death entries, dialogue, stone labels): question 24.

## Index

**Characters**
- [The Wanderer](Characters/the-wanderer.md): the player, a former war chaplain; his arc and the story.
- [The testament king](Characters/the-testament-king.md): his reign, his death, "Not him".
- [The court keeper](Characters/the-court-keeper.md): the "him" in "Not him".
- [The Unfallen](Characters/the-unfallen.md): the Crimson prisoners, their jailers, the six.
- [The first keeper](Characters/the-first-keeper.md): the first boss.
- [Villagers](Characters/villagers.md): peasants, monks, guards, barterers; lines.
- [Hollows](Characters/hollows.md): Hollows, loose souls, kill / burn / bind, the Misborn and other creatures.

**Organizations**
- [The Order](Organizations/the-order.md): its layers and who knew.
- [Keepers](Organizations/keepers.md): the dark monks, old and young.
- [The Crimson Circle](Organizations/the-crimson-circle.md): who sealed the Unfallen.
- [The king's readers](Organizations/the-kings-readers.md): the inner circle the Circle grew from.
- [The crowns and heirs](Organizations/the-crowns-and-heirs.md): the war's sides; the heirs are the king's two sons, whose claims outlived them.

**Runes**
- [What runes are](Runes/what-runes-are.md): names, tiers, look, shards, carving.
- [Blanks](Runes/blanks.md): how stones are made.
- [Origin of runes](Runes/origin-of-runes.md): the false rites, the relic doctrine, the trade.
- [Willing and forced](Runes/willing-and-forced.md): downsides, the wire.
- [Crimson](Runes/crimson.md): the prison runes and what the Wanderer can do with them.
- [Fusing](Runes/fusing.md): two souls per stone at most, the 28 kinds and their traits; Crimson can't be fused (round 42).
- [Rebuilding and binding](Runes/rebuilding-and-binding.md).
- [Root names](Runes/root-names.md): proposed new rune types; root name = strongest verb at death.
- [Rune types](Runes/rune-types.md): three families, one per Quiet god; folk grades (round 41); the mapping and spine-and-marks glyphs (round 42).

**Mechanics**
- [Corruption](Mechanics/corruption.md): the meter, the Whisper, the Pull.
- [Uttering](Mechanics/uttering.md).
- [Offering and favour](Mechanics/offering-and-favour.md).
- [The six rites](Mechanics/the-six-rites.md): rites and souls' needs.
- [Reading and echoes](Mechanics/reading-and-echoes.md): reading, the doctrine, stone-sickness.
- [The living binding](Mechanics/the-living-binding.md).
- [Death](Mechanics/death.md).
- [Currency and barter](Mechanics/currency-and-barter.md).
- [Persistence](Mechanics/persistence.md).

**Gods**
- [Overview](Gods/overview.md): the pantheon, the good death, what feeds each dark god.
- [Ennick](Gods/ennick.md) · [Gled](Gods/gled.md) · [Wend](Gods/wend.md) · [Hush](Gods/hush.md) (and the Greying) · [Grudge](Gods/grudge.md) · [Mortmain](Gods/mortmain.md)

**Locations**
- [The land](Locations/the-land.md): time, place, name, reckoning.
- [Battlefield](Locations/battlefield.md) · [Rot Swamp](Locations/rot-swamp.md) · [Chapel Ruins](Locations/chapel-ruins.md) · [Ashen Forest](Locations/ashen-forest.md) · [Frozen Pass](Locations/frozen-pass.md)
- [Villages](Locations/villages.md) · [Mother House](Locations/mother-house.md) · [Court chapel](Locations/court-chapel.md) · [Wayside shrines](Locations/wayside-shrines.md)

**Timeline** ("now" = year 0)
- [Before the king](Timeline/before-the-king.md) · [The king's reign](Timeline/the-kings-reign.md) · [The testament war](Timeline/the-testament-war.md) · [After the war](Timeline/after-the-war.md)

## Glossary

- **Name:** what a thing does, given a shape. Root names (Rend, Ward, Hunger), names of kinds, and true names of noted individuals.
- **Rune:** a name written in stone holding a trapped soul; glow = tier (strength of the bound name), glyph = type.
- **Family (of a rune):** one of three, one per Quiet god; decided by what the man was doing as he died: refusing (Grudge), clinging (Mortmain), slipping away (Hush). The god who wants the soul most; Mortmain still holds every forced stone. The subtype is the root name, his strongest verb at death: Grudge {Rend, Break, Sting}, Mortmain {Ward, Still, Sink}, Hush {Hunger, Flee}. Shown as the glyph's spine, the subtype as its marks. (rounds 41–42)
- **Biter / holder / taker:** the gleaners' folk grades for the Grudge, Mortmain and Hush families; shown on stones until the Wanderer learns the god, then the label turns to the god (round 41; the turn is flagged against round 48's no-god-names rule).
- **Blank:** a keeper-made stone, the one thing only a keeper can make; with the withholding rite it takes a soul. The crown or company paid keepers for blanks and handed them to chaplains with their wages; captains took them for prayer stones. (rounds 36, 38b)
- **Rune Shard:** feeds a rune's growth; spent to carve and fuse; returned when a rune is uttered. Not soul.
- **Notch:** a carved mark on a rune's edge; one per level of growth, max five.
- **Fusion:** forcing two souls to share one stone; two souls at most, so a fused stone never fuses again and Crimson (jailer + prisoner) can't be fused. Two different subtypes, families may cross; higher tier sets the glow; each half works at 75%; named for the kind the pair spells ("Rune of the Wolf"), with that kind's one trait. Three gates: type, compatibility (a fact about the souls), consent (willing + willing only); only the type gate is built. Only a forced result adds corruption; a refused fuse is wired by the Wanderer with iron scrap. (rounds 14–15, 42)
- **Kind (of a fused rune):** the name two root names spell together, e.g. Wolf (Rend + Hunger), Ox (Break + Ward), Crow (Hunger + Flee); 28 in all, each with one trait. (rounds 3, 42)
- **Consent (fusing):** whether two willing souls agree to share a stone; learned by reading both. (round 14)
- **Compatibility (fusing):** whether two souls can share a stone at all; a fact, not will. (round 15)
- **Loose soul:** the soul of a rune broken unspoken (or a cut-short rite with no blank); walks the nearest unburned corpse as a Hollow; killed, it rises again in the same body after a long window; burned, it takes the nearest unrisen man's corpse, else a beast's (Misborn), else drifts; only binding catches it. Killing and burning cost no corruption; binding does. (rounds 8–10, 13, 15, 36, 49)
- **Misborn:** a man's loose soul in a beast's corpse, when no man's corpse is left; bred by plain burning, never by Gled's fire. E.g. a dead warhorse forced upright, helmet rammed on its skull, screaming in a man's voice, one word when it dies. A beast's soul never takes a man's body. (round 49)
- **At rest:** an area whose souls are all bound or burned. (round 49, design intent)
- **Rite cord:** a knotted cord tied at the dying man's wrist; its knots are a number, looked up in a chapel ledger or with a monk. (rounds 13, 19)
- **War chaplain:** a monk who gave the field form on the battlefields; the Wanderer was one. Learned both forms. (rounds 9, 16, 38)
- **Field form / withholding rite:** the rite cut short before the release; Mortmain's craft; taught to chaplains as the war's hasty dispensation. (rounds 19, 28, 36, 38)
- **Long rite:** the full last rite, ending in the release; a full good death. Chaplains learned it beside the field form. (rounds 27, 38)
- **The prologue:** the game's playable opening, ~3 years ago: the mad, starving chaplain at the Pull reads a wired Pale Rend by cutting with it; no echo comes, but reading touches the soul and he recognises a name he spoke ("I know this name. I said it."). (rounds 38, 38b)
- **Rune-currency:** finished stones bought by the crowns with silver, as weapons, war chests and ransoms, once the kingdoms learned to wield them; drove trapping for profit. Never wages (always coin). Ended when the crowns' silver ran out (~11 years ago); unsold stones piled in chapel naves and lay on the fields. Only the Paymaster paid his men in stones. (rounds 16, 38b)
- **Relic doctrine:** the Order's teaching that a stone is a harmless relic left after the soul goes free. (round 17)
- **The Greying:** the world's loss of color; what no one remembers greys; rune color is the last of what is remembered. Hush's. (rounds 16–17)
- **The good death:** the Naming (Ennick), the Letting Go (Gled), the Walking (Wend). (round 18)
- **Keepsake:** the one small token each family kept of its dead; Mortmain hid in it; stones were believed because they looked like keepsakes. (round 18)
- **Patient gods:** the good gods: Ennick of the Knots, Gled the Pyre, Wend the Road Home.
- **Quiet gods:** the dark gods: Hush, Who Eats the Name (eats names; the forgetting); Grudge, the Kept Coal (eats a soul's refusal; uttering's scraps, hatred Hollows, "Not yet"); Mortmain, the Dead Hand (eats a soul's freedom; blanks, the withholding rite, wire, the trade, the keepers; his rite locks a soul forever). (rounds 17–19, 36–37)
- **Dark rites:** the three rites of the Quiet gods; each consumes the soul (locked, eaten, twisted); each eases the Pull more than uttering; a known dark monk performs them for metal. (round 19)
- **Need (of a soul):** what a trapped soul lacks of the good death: its name, letting go, someone to let it go, or just the road; finished in order, ending at Wend's road. (round 20)
- **Echo:** the cryptic line a read rune gives. A forced echo is fixed and nameless because Mortmain withholds the name; it changes only when part of the soul's need is finished; goes silent while Hush quiets the stone; stops at the Pull; can be misheard in the Whisper. A willing stone speaks its own name. (rounds 20, 25, 37)
- **"A shriving hand holds no stone":** the Order's rule that kept chaplains from reading stones. (round 25)
- **Stone-sickness:** the Order's cover for killing men who asked the right questions. (round 25)
- **"Not yet":** Grudge's favour; once, for a while, a killing blow leaves the Wanderer on a sliver of health. (round 19)
- **The Whisper / The Pull:** corruption at 75–99% (the world's text lies; found shrines stay put) and at 100% (madness: stronger, free utterances; withdrawal that outweighs them). (rounds 9–10, 13)
- **Iron wire:** binds every forced stone, drawn from the dead man's own mail. Iron is the jailer's metal, a truth only the Wanderer learns. (rounds 10, 22)
- **Iron (as money):** refused for a glut and for wire money; still scrap for nails and hinges. (round 22)
- **Wire money:** the war's last silver marks, iron-cored under a silver wash. Why every coin is nicked. (round 22)
- **Crow / mark / head:** the old coins: bronze, silver, gold. Pass only by weight, most of them cut. (round 22)
- **Resonance:** a named effect from runes set together in one piece of gear.
- **Crimson Circle:** the king's former inner circle of readers, who knew what stones are and chose stone anyway; they made the willing runes and gave themselves as Crimson jailers. Most are spent; the handful left are taken for ramblers. (rounds 17, 35, 37)
- **Crimson:** a unique prison-rune holding a willing jailer's name and an Unfallen prisoner's. It can be lashed, uttered (consumes the jailer, frees the prisoner to fight), released at a shrine (frees the jailer, prisoner fought), never offered. (rounds 30–31)
- **Unfallen:** men Grudge would not let die; Grudge's living coals; the Crimson prisoners. (rounds 30, 37)
- **Last rites (false):** the rite for the dying, believed to free the soul; it traps only with a blank in the dying man's hand. Souls so taken count as forced. (rounds 7–8, 36)
- **Reading:** learning a rune by doing what it names; personal.
- **Lash / lashed:** a stone lends its verb only when lashed against bare steel: three spots on the blade (left guard arm, right guard arm, ricasso), two on the armour (where the straps cross bare plate, for Ward). Forced stones are tied with their own wire tail; willing stones with cord, gut or thong. No changing stones with Hollows near. Replaces "socket" in canon; the code still says socket. (round 39)
- **Utterance:** speaking a lashed rune's name through the blade; burns the soul for a spell, shatters the rune, returns shards, adds corruption; Grudge eats a scrap of the rage, and his leftovers rise as a hatred Hollow. (rounds 10, 37; built round 48, keys 1–5, see [Uttering](Mechanics/uttering.md))
- **Freeing:** finishing what a soul lacks, ending with Wend's rite at a wayside shrine; the only thing that lowers corruption. (rounds 7–8, 19–20)
- **Gratitude:** the name for what lowers corruption. Not a separate meter. (round 8)
- **Offering:** Hush's rite; the name is forgotten even by kin, the soul consumed, the rune destroyed; no shards, no Hollow; more corruption than an utterance; eases the Pull more; earns quiet stones. (rounds 6–13, 19)
- **Favour:** a dark god's thanks for his rite: Hush, quiet stones; Mortmain, dark monks warm to him; Grudge, "Not yet". Scales with tier; always true. (rounds 12–13, 19, 21, 37)
- **Living binding:** binding a living person's name without consent; only as a dark rite; the victim goes hollow; the heaviest corruption. (round 21)
- **Spent / forgotten name:** an uttered name is spent (remembered, names nothing); an offered name is forgotten. (round 12)
- **Binding:** trapping a soul in a stone; costs corruption. At a laid-down body before it rises (a breath), a true blank takes the soul present, giving an unread forced stone (round 49). By name, an empty rebuilt stone calls the soul from wherever it is; the result shows where it was (round 13).
- **Carver:** the village monk, who patches shattered runes with mortar for metal. (rounds 5, 37)
- **Chapel ledger:** a record of names in the Chapel Ruins. (design canon) Every village keeps its own ledger too (round 47).
- **Corruption:** the Wanderer's one meter; follows acts, not intent; starts around 25–35%; lowered only by freeing. (design canon)
- **Willing / forced rune:** a soul that came willingly (bare, no downside, speaks its name) or was trapped (wired, a downside from Mortmain's grip, growing with tier). (rounds 6–10, 37)
- **Wayside shrine:** a roadside altar of the good gods where souls are freed. Every village has one just inside its south gate (round 47).
- **Hollow:** a risen husk walked by a loose soul, or a hatred Hollow raised from an utterance (nameless, ember, stays dead, no body). All enemies are Hollows in different bodies: men, beasts, Misborn; most bosses too, except the living keepers and Unfallen. (rounds 10–13, 49, 49b)
- **Scrap:** Rusted Blade ("Snapped near the hilt."), Dented Helm ("Its owner didn't need it."), Cracked Plate ("Pierced through the heart."). (seen in: items.js)
- **Bronze / Silver / Gold:** metals counted in grams, the only currency. (rounds 22–23)
- **Grave coin / road coin / eye-coin:** a crow on each eye of the dead, the kin's gift for Wend's road; Wend asks no fee. (round 23)
- **Rite fee:** the metal a family pays a monk for a proper last rite. (round 23)
- **"The road carries only the man":** the low-corruption death rule; the bag stays where he fell. (round 24)

## Questions waiting for the user

Resume here. Recommendations in brackets.

1. **The Circle's runemakers** (round 37 proposal a): were the Order brothers among the king's readers honest monks the keepers taught, so "making always took a keeper" becomes "only the keepers and the few they taught"? [Yes.]
2. **Who trapped the beasts** (round 37 proposal b): the keepers (round 34 canon) or the readers themselves (the user's round 37 story)? [The readers, so their jailing is atonement; it means editing round 34.]
3. **Reading A:** the withering and famine come before the king's death. [Yes.] And "blight" vs dead yokes as the hunger's cause. [Dead yokes, with blight as a later bad year.]
4. **How the other crowns and the heirs were forgotten.** [Their stones were offered to Hush too.]
5. **History review leftovers:** the king asking a known keeper for the true rite [the stayer hid even from the king]; the Mother House's fall [cleared like the chapels]; who held the king's stone [the court chapel]; when the doctrine was written [when the Order began selling]; extra king's-guard Crimson stones beyond the six [yes].
6. **The land's folk name** (the Wake?) and the no-year reckoning. (round 32)
7. **The living binding:** Mortmain as owner, "Take him in hand" at his niche with something the victim owns, learned through C2 fooled once; the stone freeable only after the husk is burned [recommended] or permanent?
8. ~~New root names~~ settled: Break, Sting, Still, Sink and Flee built (round 42, via question 17); strongest verb at death settled round 41. Watch stays unbuilt.
9. **Grudge proposals** (round 37): he keeps wars going; the Letting Go starves him. [Both yes.] Willing utterance raises no Hollow. [No.]
10. **Round 38 knock-ons left:** whether the Pale Rend's echo becomes a later beat below the Pull. New from round 38b (flagged, not settled): (a) the long rite "counted as Wend's rite" with no shrine, vs round 20's "falls only through Wend's rite at a wayside shrine"; and since the in-play reason is now scarcity, would a dying man met in play still lower it? (b) the chapels fell ~10 years ago with the keepers gone, yet unsold stones "piled up in chapel naves" after; who carried them there? (c) silver runs out ~11 years ago, crowns stop buying ~10 (one-year gap). (d) what the Paymaster's men did with stones nobody would buy (wield them?).
11. **Prologue text** (round 38c): the name in the Rend stone (placeholder "Aldric Venn"). The sons' fate (round 38e settled only that both died before the war ended, their claims passing on): when and how they died, and whether their souls were stoned; ties into question 4.
12. **Round 39 leftovers.** (a) Smithed settings as a rich man's fitting? Decides whether the king's champion "socketed" (round 27, two places, flagged) stays or becomes "lashed". [Yes, rare: forged sockets on lords' and champions' blades, which is why "socket" survives as a rich man's word.] (b) The shriving pair prop ([Battlefield](Locations/battlefield.md)): accept the proposed look (soldier on his back gripping an empty, unglowing blank, chaplain fallen across him, empty hands)? Can the blank be taken? [No: an empty blank would be the one thing only keepers make, loose in the player's hand; his fingers won't open.] (c) "The dead are burned" vs the Frozen Pass cairns and ice tombs, and Crimson's "the sacrifice's grave". [The pass has no wood; the ice is the only fire there. Reword "grave" to "pyre place".]
13. **The arc's spine** (round 40, [The Wanderer](Characters/the-wanderer.md)): S1 "The Count" (find and free his own dead; the Mother House holds his count), S2 "The Words" (find who wrote the short rite) or S3 "The Last Blank" (stop the making)? [S1.]
14. **The endings** (round 40): decided when the court keeper falls; below 75%, released gives E1 "The Count", uttered gives E2 "The Sentence"; at 75% or more, the god he fed most gives E3 "The Niche" (Hush and Mortmain) or E4 "The Coal" (Grudge: he becomes Unfallen and the last Circle member seals him). Keep all four? [Yes; E4 needs the rambler seeded early.]
15. **The abbot** (withheld since round 28): did he know? [No. He believed, like the Wanderer; his stone repeats the doctrine. Guilty by acts, not intent.]
16. ~~What decides a stone's family~~ settled round 41 (see [Rune types](Runes/rune-types.md)).
17. ~~The mapping~~ settled round 42: Grudge {Rend, Break, Sting}, Mortmain {Ward, Still, Sink}, Hush {Hunger, Flee}, spine-and-marks glyphs, built (see [Rune types](Runes/rune-types.md)).
18. **Fuller favour** (first half, folk grades first, settled round 41): does giving a stone to its own family's god give fuller favour and ease the Pull more? [Yes, same corruption.]
19. **Round 42 flags** (see [Fusing](Runes/fusing.md) Open): (a) kind names already mean beasts (round 3 "every wolf shares one", round 34 beast stones): is a Rune of the Wolf two men who spell "wolf", and how does it differ from a true (Pale) beast stone? [Two men; the kind is the shape their verbs make together, which is why the old readers called beasts by the same names. A beast stone is one soul, already whole, and can't be fused.] (b) Bramble, Sundew and Oak have no souls: are names of kinds for anything that acts? [Yes, names are "what a thing does"; nettle already counts for Sting.] (c) Kinds overlap the built resonances: Beetle = Leech-shell (overhealing becomes a shield), Wolf ≈ Bloodletting, Ox ≈ Bulwark; and "Leech" is both a kind and part of a resonance name. [Design call; rename one side.]
20. **Echo pool repeats** (round 44): many stones share each of the 8 lines per verb. Accept as in-world ("men die alike"), split echoes into two fragments, or keep kin and places only on clue stones? [Two fragments, plus the in-world line.]
21. ~~The Wanderer's book~~ settled round 46: his office book, belt-chained, Whisper entries kinder, Pull hand broken, plain-hand margin notes (see [The Wanderer](Characters/the-wanderer.md)). Left over: (a) names written only after the game gives them as exact strings, never a source [yes]; (b) long rite pages read blank at the Pull until he kneels [yes]; (c) a separate Whisper-death entry, since Wend doesn't send him back there [yes, "death_whisper" in journal.json].
22. **Empty stones at the stall** (round 49b: true blanks are sold at the village chapel; only the barterer's text is left to fix) (round 46 flag): godot/scripts/game/items.gd says the barterer sells empty stones, but the barterer's dialogue says "No stones at my stall." [Sell them through the village monk, who patches them.]
23. **Round 47 flags** (villages hold all rite places; see [The six rites](Mechanics/the-six-rites.md), [Villages](Locations/villages.md)): (a) ~~a stranger at the village's rite places~~ settled round 48: he can, because he is an ordained chaplain. (b) and (c): the user "will decide". (b) Hush's rite at every village ledger vs round 12's offering at a spent reliquary below 75%. [Both work; the ledger is Hush's rite, the reliquary his old larder.] (c) dark rites usable before "fooled once" teaches them? [Greyed until learned.] (d) why Grudge's Hollow rises past the wall. [Nearest unburned body; inside, the dead are burned.] (e) ~~nothing lowers corruption at the Pull~~ settled: a good rite at the Pull costs blood (a flat health cost for now).
24. **No god names: scope** (round 48 flags; see [The six rites](Mechanics/the-six-rites.md) Open): (a) does the stone's folk grade still turn to the god once learned, or stay biter / holder / taker for good? [Stay folk grades; the god is learned from the world, never labelled.] (b) the book's death entries name Wend twice ("Wend walks the dead home."): reword? [Yes: "The road walks the dead home."] (c) does the rule cover villager speech? The dialogue data names the gods often. [Villagers may name the good gods as folk do; nobody names a Quiet god.] (d) in-world reason a chaplain doesn't name gods he knows: [The Order's "Say the work, not the name": a name spoken is a name spent.]
25. **Uttering flags** (round 48; see [Uttering](Mechanics/uttering.md) Open): (a) the Hollow barrier makes uttering inside a village safe: hatred Hollows ignore the barrier, or rise past the wall? [Ignore it; the guard's line earns its keep.] (b) a fused stone burns two souls but raises one Hollow. [One Hollow at the higher tier, double ember.] (c) armour stones uttered vs "through the blade". [Reword: "through the steel it's lashed to".] (d) Hollow strength by tier, not spell power. [Accept: "by the soul's tier".]
26. **Round 49 leftovers** (see [Hollows](Characters/hollows.md) Open; c, d, e settled round 49b): (a) binding at the body vs binding by name: keep both? [Yes.] (b) **prologue redesign:** the deliberate binding vs "he still doesn't know the field form traps"; the user will decide the new scenes [he does it as the field form, from habit]. (f) why Gled's fire breeds no Misborn [it cuts the soul's grip on any flesh; it drifts until bound by name] ([Gled](Gods/gled.md)). (g) the Misborn's word and stone: open until beast runes are decided. (h) true blank vs patched stone [blank binds at the body at full tier; patched binds only by name, one tier lower] and who makes the chapel's blanks [war stock sold by an ordinary monk; a dark monk may make more] ([Rebuilding and binding](Runes/rebuilding-and-binding.md)). (i) a chapel in every village vs "at most one monk" ([Villages](Locations/villages.md)).
- Still queued: binding a Grudge-twisted soul (nothing answers, or ember?); failed fuse A (A1 leading); is the wire on a bound willing volunteer?
