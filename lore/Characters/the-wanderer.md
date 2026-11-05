# The Wanderer

The player. A former war chaplain who gave the last rite to the dying by the thousand, out of duty, never knowing it trapped them. The trapping drove him mad by the war's end; he came back by giving the long rite to the dying for three years. Now he scavenges the ruins for runes and slowly learns what his rites really did. The stones he finds may hold men he shrove himself.

![The Wanderer](../images/wanderer.png)

## Canon

- **A lone warrior with an oversized greatsword and heavy armor.** Blade: three rune spots (Rend, Hunger); armor: two (Ward). Four-hit combo and a dodge. (seen in: wanderer sprite, combat.js, runes.js; the code still says "sockets")
- **Runes are lashed, not socketed** (round 39). A stone lends its verb only when it is lashed against bare steel. **Blade, three spots:** the left guard arm, the right guard arm, the ricasso. **Armour, two spots:** Ward stones are lashed where the straps cross bare plate. "Lash" / "lashed" replaces "socket" / "socketed" in canon. See [What runes are](../Runes/what-runes-are.md).
  - **Forced stones are tied with their own wire tail;** willing stones are bare, so they need cord, gut or thong. (round 39)
  - **No changing stones with Hollows near** (round 39, design canon, not built).
- **Stays the player character and a melee fighter.** Magic only as utterances through the blade. (round 2)
- **A former war chaplain** (round 9): gave the last rites on the battlefields, not knowing the rite trapped them. (Settles round 8's "one of the monks".) **At the start he works against what he senses is wrong,** by giving proper rites; he learns later that it is the dark gods. (round 38b, rewording round 9's "works against the dark gods")
- **He was paid in coin like any soldier;** his blanks came with his wages as tools of the rite, and he took them for prayer stones. (round 38b)
- **He served out of duty, not understanding.** He gave the rite by the thousand because it was his office. (round 16) The free rite in the war was the false one (round 23). He said the field form; the dying man gripped a keeper's blank (round 36).
- **He was not the king's chaplain.** (round 27)
- **Age** (TB, round 34): about 45; a chaplain from about 22 to the end of the war. He trained beside the Paymaster's chaplain (round 31).
- **He carries corruption** that rises with every soul he spends or traps. (rounds 6–8) **He starts the game at about 25–35%.** See [Corruption](../Mechanics/corruption.md).
- **He went mad by the war's end** (round 38). Corruption follows acts, not intent: thousands of trappings put him at the Pull (100%) by the war's end, ~3 years ago. **He was sane for most of his service:** he crossed into the Whisper late and hit the Pull on or near the last field. (round 38b)
- **He doesn't remember the names he spoke.** A name comes back only through reading the rune that holds it. His memory isn't a binding source. (round 10) **Round 38b, how this works at the Pull:** reading means doing what the rune names, and that still works at the Pull; only the echo stops. Reading puts him in touch with the soul, and because he spoke this exact man's name in the field rite, the name comes back to *him*. For anyone else a forced stone stays nameless. Plain memory without reading still gives nothing, and memory is still not a binding source. No conflict with round 10.
- **The break with the doctrine is staged** (round 25; more stages allowed):
  1. **The prologue, ~3 years ago, at the Pull: a crack he can explain away** (round 38; moved from "the first screen"). Under "A shriving hand holds no stone" he has never held one. Mad and starving from withdrawal (round 38b), he breaks the rule: he takes a wired Pale Rend from a dead man, lashes it to his blade and cuts with it until it reads, the first reading of his life. Echoes stop at the Pull, so the stone gives no echo. **The reading puts him in touch with the soul, and the name comes back to him because he spoke it in the field rite** (round 38b). That wakes him. The soul's need is separate and comes later. Message, his own thought: **"I know this name. I said it."** (Name: an exact game string, not chosen.) The doctrine still covers it: the track of a man he shrove.
  2. **Mid-arc, the real break.** After he finishes a step of a soul's need, its echo is different. Proposed message: "The words in the stone are different." His line: "An echo does not answer."
- **The prologue's text, in the game** (round 38c, design canon; seen in: godot/scripts/prologue.gd INTRO and the prologue beats). Opening narration, his voice, one line per card:
  1. "A king died and said two words: Not him." 2. "His sons each swore it meant the other. We fought a generation over it." 3. "I was a chaplain. I knelt by the dying and said their names, and the short rite." 4. "The war had no time for the long one." 5. "Thousands. I did not count them." 6. "The dead did not stay down." 7. "Then the war did not end. It ran out." 8. "And something in me went wrong." (Lines 1–8 approved by the user; 6 and 7 swapped round 38d so the dead rise during the war, as rounds 10 and 26 say.)
  9. "The colour went out of things first." 10. "Then the long words. I knew them by heart, and they would not come." 11. "I was hungry, and food did not help." 12. "I wanted to kneel again. I did not know to whom." (Lines 9–12: what he felt going mad; the user asked for them, written from rounds 9/20/38b canon.)
  - **"His sons"** (round 38d): the heirs are the testament king's two sons. See [The crowns and heirs](../Organizations/the-crowns-and-heirs.md).
  - **Line 9 is his own felt version of the Pull's dimming, not the Greying** (round 38d). The world's grey is still Hush's forgetting; this is how the dimming felt from inside.
  - **Line 12's kneeling is a deliberate echo** (round 38d): here kneeling is the craving; in play, kneeling at the Pull is how he forces the good words back (round 20). Same act, turned the other way.
  - Gameplay opens: "The last field. No one came to say it was over." Taking the stone: "A shriving hand holds no stone." / "I hold it anyway." Reading: "The stone reads. It says nothing." Then the name, then "I know this name. I said it." Card: "Three winters later."
  - **The lashing beat** (round 39, design canon): he pulls the stone's wire tail with his teeth and winds it round the ricasso; the first turns slip; he pulls it tight. Then the dead rise, and he cuts until it reads.
  - **The name in the stone is a placeholder** ("Aldric Venn" in the code). Not canon; the user must choose it.
  - **Round 49 additions** (design canon, the user): the dead he kills keep rising, in the same bodies; he is grim and resolved, not frantic. The first name he reads is a man he shrove himself (as round 38b). The dead rise again quickly here (round 49b). One of the first corpses he laid down gives a breath; he takes a blank from his own bag, traps the soul in it, and so gets his **second rune, unread.** See [Hollows](hollows.md).
- **The three missing years** (round 38; ~3 years ago to year 0): woken, he gave the **long rite**, done perfectly and without haste, to the dying he met. At first out of guilt, after seeing bodies everywhere; then for peace, because the more he did it the more peaceful he became. At the Pull every good rite cost blood (the kneel). A full good death given to a dying man without a blank counted as Wend's rite, so his corruption fell slowly to 25–35% by year 0.
- **He barely survived the withdrawal** (round 38b). He arrives at year 0 thin and worn.
- **He still doesn't know the field form traps** (round 38). He felt peace, not understanding. The staged break stays intact.
- **What he knows at the start** (round 38b): that *something* was wrong with the field form (why he chose the long rite for three years), not *what*.
- **Backstory only** (round 38): in play, the long rite to the dying does NOT lower corruption. Only freeing at Wend's road does. **Why** (round 38b): the war gave him endless dying men; now few die near him, and villages have their own monks, who gave the rites to their ancestors, so they'd rather have them than a stranger.
- **He may perform the rites at any village's ledger, fire and road shrine,** because he is an ordained chaplain (round 48, the user). See [The six rites](../Mechanics/the-six-rites.md).
- **Death and return:** see [Death](../Mechanics/death.md).
- **His book** (round 46; the user's idea from round 45). **Canon:** it is his chaplain's office book (option A): the long and the short rite, and ruled pages at the back for the names of the shriven, which he never filled ("Thousands. I did not count them."). He fills them now. **Scope** (the user): it covers everything that adds flavour to the character and the story: echoes heard, notes on what he lives through (written automatically, in his voice), and the player's own notes. (seen in: godot/scripts/game/journal.json, being built)
  - **Accepted design** (round 46, not built yet):
    - **Worn, not carried:** chained to his belt, so it comes back with him on death like sword and plate, and the dark gods never take it (it holds no soul).
    - **He writes only what he believes at the time.** Early entries call stones relics and echoes tracks; nothing in them goes past the staged break.
    - **The Whisper:** entries written at 75% or more read kinder or a little off, never false names. Entries written below 75% stay true (memory beats the lie, as with found shrines). Back below 75%, the Whisper entries stay as he wrote them.
    - **The Pull:** the hand breaks; entries go short and shaky; no echo entries (echoes stop).
    - **Player notes** go in the margins in a plain hand, never voiced and never changed by corruption.
  - **Entry text is game data**, his claims at the time, not canon facts (like the echo pool).

### Story (round 8, 9, 16)

- **Main arc:** not fully established. Crimson bosses carry large steps of story. (round 8)
- **The arc of understanding** (round 16) is the spine: he slowly learns what runes are and what his rites did.
- **His role:** scavenging the ruined world for runes, metal and scrap, trading in rare villages, working against what he senses is wrong (the dark gods, though he learns that later). (round 9, reworded round 38b) The game opens with a playable prologue at the Pull (the mad chaplain on the field reads the Rend stone), then cuts to year 0 in a village at 25–35%. (round 38)
- **A slow reveal:** which monks serve the dark gods is uncovered over time. (round 7)

## Open

- **Prologue redesign (open, round 49b: the user says the new prologue scenes still need deciding). The prologue binding vs "he still doesn't know the field form traps"** (round 38) and "something was wrong with the field form" (round 38b). Trapping a soul in a blank on purpose looks like knowing. Proposal: he does it from habit, as the field form over a man already down, believing he shrives him; only later does he learn the two are the same act. Also: he is a chaplain who refused the short rite for three years after this, yet does it here; the madness of the Pull can carry that.
- **The main story arc and the ending(s)** (ranked 1 in the old list). Everything feeds it. Endings for the Greying: see [Hush](../Gods/hush.md). **Round 40 proposals below; nothing chosen.**

### Round 40 proposals: the arc's spine (not canon)

- **S1, "The Count" (loremaster's pick).** Prologue line 5 says "Thousands. I did not count them." The arc is him learning that someone else counted them for him.
  - **Year 0 want:** find out what was wrong with the short rite. Practical form: find the rite ledgers that hold his war cords and see what was written against them (a chaplain checking his own books). That sends him to the Chapel Ruins.
  - **First keeper and the sale-book page:** the page lists cord numbers with a grade, a buyer and a price in marks. Proposed detail: each chaplain was issued his own run of cord numbers, like a ticket book, and he knows his run. "Those are my numbers." Want becomes: where did my men go? (He can still believe they were sold relics.)
  - **Mid-arc echo change** ("An echo does not answer."): they are inside. Want becomes: find my dead and free them.
  - **His own stones answer him:** canon (round 25) says a forced stone gives its name only to the man who spoke it. So stones he shrove come named for him; their Naming is already done. His guilt is his tool, and the player can tell "his" stones from the rest.
  - **The six Unfallen:** name pieces and the way to the Mother House. The Paymaster's chaplain, who trained beside him, is his mirror: a chaplain who learned and chose stone. Proposed parting echo: "You said the short words too. I counted mine."
  - **Mother House and the abbot:** the master ledger holds his whole run: the count. Proposed abbot reveal: he did not know; he believed, like the Wanderer. His stone lies in the ledger room and its echo is the doctrine itself ("A man would answer. A stone repeats."). No one at the top to blame.
  - **Court keeper, last:** "Not him" was a dying man accusing the monk at his bed of doing exactly what the Wanderer did a thousand times. The one honest verdict on his office. The last choice: release the witness or utter her.
  - **The ledger tells who bought a stone, not where it is now** (the crowns are gone, stones lie in naves and fields), so it is a count, not a map.
- **S2, "The Words."** Want: find who wrote the short rite. A chase up the chain (chaplain, gleaner, reliquary, Mother House, abbot). Weak: the keepers have no leader and the gods never speak, so the chase ends in an empty room; it is revenge-shaped (close to Guts and Griffith); and it makes killing keepers the goal, which corruption punishes.
- **S3, "The Last Blank."** Want: stop the making. He finds young keepers still pressing blanks into poor men's hands and hunts whoever makes them. Weak: any keeper can make a blank anywhere, so there is nothing to smash; it makes him an inquisitor (canon: there are none); and today's trapping is small next to the dead already in stone.

### Round 40 proposals: the endings (not canon)

Decided when the court keeper falls at the Mother House, from what the player did, never a menu. First by corruption at that moment, then by one act.

- **E1, "The Count."** Corruption below 75% and the court keeper **released.** The witness's parting echo tells the truth of "Not him". He carries the master ledger out. Freeing goes on after the credits (it is the same loop). Last image: a grey road, a small fire on a wayside shrine, an old man with the ledger on his knees, a few pages ticked, most not. Card: "Thousands. I did not count them." then "I count them now." The grey stays; the names are no longer lost.
- **E2, "The Sentence."** Corruption below 75%, court keeper **uttered.** A sure win, and the witness is spent. Her last echo is cut off mid-word ("It was not—"). He knows the truth and can never prove it. Last image: on the road out, a boy cutting "Not him" into a new milestone, the way his father did. The war's sentence outlives everyone.
- **E3, "The Niche."** Corruption 75% or more, and he fed **Hush and Mortmain** more (offerings, bindings, rebuilds, forced fuses, niche rites). The undercroft keepers know him and do not fight; he stays. The ending text is shown through the Whisper's kind words ("He kept them safe."), while the image shows the truth: he scrapes the master ledger page by page (Hush's ledger rite), and his face blurs. Then a village, a cheap monk, a blank pressed into a dying hand.
- **E4, "The Coal."** Corruption 75% or more, and he fed **Grudge** more (utterances, pyre rites, Crimson stones uttered). "Not yet" keeps landing until death will not take him: he has become Unfallen. A rambler villagers mocked all game, the last of the Crimson Circle, kneels with a blank and cord: "Two names. One yes." Last image: two bodies in the nave, hers still and his breathing, a crimson stone between them, a crow. (Fits round 4: the player never performs the sacrifice; here he is the prisoner.)
- **Seed for E4:** the rambler should be met early. Proposed villager line: "She asks the names of the dead and knots them in a cord. Mad."
- **Loremaster's objection to S1:** it reruns the backstory. The three missing years were already a penance that ended in peace. Fix: the game is the undoing of that peace (he found it through not knowing); no ending gives it back. Also, tallies decide E3 and E4, which is a hidden morality score; keep it readable in the world (ticked ledger pages, quiet stones, embers in his wounds).
- **The stone's echo as a later beat** (round 38 proposal, not canon): "He said my name. Then nothing." comes the first time he reads a stone below the Pull.
- **Why a chaplain carries a greatsword and plate.** Proposal: chaplains rode with the companies and were armored like them; the blade was taken from the field.
- **His own iron:** he wears plate in a world that won't trade iron. Proposal: guards eye it ("Keep your blade low inside the walls" fits).
- **Tension, kept on purpose:** a monk against the dark gods who burns souls (uttering) and binds names (rebuilding) still does their kind of work. The dark monks want him to go one step further and offer.
- **The name in the Rend stone** (round 38c): "Aldric Venn" is a placeholder; the user hasn't chosen.
- **Prologue text notes** (round 38c, no clash): line 1 "died and said" is the common telling (the war was really fought over the stone's certified echo; the narrator needn't know the difference). "A generation" matches canon (~28 years).
- **Line 9 risk, still to watch** (round 38d): players may read the grey world as his madness. Canon says the grey is the Greying; something later in the game should show the grey stays after he is sane.
- **Smithed settings as a rich man's fitting** (round 39 proposal, deferred by the user): did lords and champions have stones set in forged sockets? Two old references say the king's champion "socketed" his Rend stone (round 27: [The testament war](../Timeline/the-testament-war.md), [The testament king](the-testament-king.md)). Left as written until this is decided.
- **The book, still undecided** (round 46; the rest is in Canon):
  - **Names:** a name is written only after the game has given it as an exact string (reading, kin, cord, ledger); the book is a record, never a source, and writing a name in it is not Ennick's rite. (Proposal; the user hasn't ruled on it.)
  - **Pre-numbered lines** with his cord run, only if S1 is chosen.
  - **The long rite pages read blank at the Pull until he kneels** (line 10). Proposal; "the broken hand" was accepted, this part wasn't stated.
  - **Death in the Whisper:** the dark gods, not Wend, send him back, so a death entry there can't thank Wend. journal.json has an extra key "death_whisper" for this; needs the user's OK and code support.
  - Rereading early entries after "An echo does not answer" as the break seen on the page (proposal).- **Echo voice:** "echoes are heard in the reader's own inner voice" is a proposal only, so "he knows the voice" is dropped: he knows the name.

## Rejected

- **The Wanderer recast as an enemy or boss; the player as a wizard** (round 1). Rejected round 2.
- **The Wanderer was the king's chaplain.** Rejected round 27: it would make the world turn on him, and under Hush he'd have forgotten anyway.
- **"His faith held the door mostly shut"** (round 11 reason for his starting corruption). Rejected round 38: it is intent under another name, and corruption follows acts. He reached the Pull and came down through the long rite.
- **First reading on the first screen, at year 0** (round 25). Moved round 38 to the prologue, ~3 years ago, at the Pull.
- **The book as a war tally book (B) or a dead gleaner's book (C)** (round 45 proposals). Not chosen round 46: B clashes with "Thousands. I did not count them."; C loses his voice and his past. The user chose A, his office book.
- **"You know this name. You said it."** (round 25 message). Replaced round 38 by "I know this name. I said it.": the old line read like the stone speaking, and the name comes from his own memory.
