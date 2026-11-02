# Fusing

Fusing forces two souls to share one stone. A stone holds two souls at most. The fused rune is named for the kind its two root names spell ("Violet Rune of the Wolf") and gains that kind's one trait. In the lore it passes three gates (type, compatibility, consent); a failed fuse breaks both stones and looses the souls. The game so far builds only the type gate.

## Canon

- **Fusing forces two souls to exist together in one stone.** It is not trapping. (round 8)
- **Two souls per stone, at most** (round 42, the user's rule). A fused rune never fuses again: "Two souls already share that stone." (Round 3's "a fused rune can't fuse again" now has its reason.) (seen in: Godot build, rune_book.gd)
- **Crimson stones can't be fused** (round 42): jailer and prisoner already make two souls. Message: "There's no room in a Crimson stone." See [Crimson](crimson.md).
- **What a fuse makes** (round 42, built in the Godot build; numbers in godot/scripts/game/rune_book.gd):
  - Two souls of **different subtypes**; families may cross (e.g. Rend + Ward).
  - The **higher parent tier sets the glow** (round 3 kept).
  - **Each half works at 75%** of a single rune of its subtype (`FUSED_SHARE`).
  - It **lashes where either half fits** (blade or armour).
  - **Named for its kind** (round 3: names of kinds are built from root names): "Violet Rune of the Wolf". Each kind has **one trait** of its own.
- **Glyphs** (round 42, built): a same-family fuse is one spine carrying both marks, on the family's stone; a cross-family fuse is two glyphs side by side on the broad tablet, joined by a crack of light (round 3's crack kept for this case). See [Rune types](rune-types.md).
- **The kinds** (round 42, built). Pair: kind, trait.

| Pair | Kind | Trait |
|---|---|---|
| Rend + Break | Wolverine | the last blow of a combo bleeds |
| Rend + Sting | Bramble | what strikes you bleeds |
| Rend + Ward | Boar | take a blow, your next hit is stronger |
| Rend + Still | Mantis | held foes take more damage |
| Rend + Sink | Pike | slowed foes bleed |
| Rend + Hunger | Wolf | hitting the bleeding heals |
| Rend + Flee | Hawk | first hit after a dodge is stronger |
| Break + Sting | Ram | strike him mid-swing and be thrown down |
| Break + Ward | Ox | can't be shoved |
| Break + Still | Badger | held foes break faster |
| Break + Sink | Elk | slowed foes are thrown down |
| Break + Hunger | Bear | breaking a foe heals |
| Break + Flee | Horse | dodge through a foe to stagger it |
| Sting + Ward | Crab | blows hurt back harder |
| Sting + Still | Scorpion | what strikes you is held |
| Sting + Sink | Sundew | what strikes you is slowed |
| Sting + Hunger | Tick | hurting back heals |
| Sting + Flee | Wasp | dodge through a foe to hurt it |
| Ward + Still | Oak | standing still hardens you |
| Ward + Sink | Toad | slowed foes hit softer |
| Ward + Hunger | Beetle | overhealing becomes a shield |
| Ward + Flee | Crayfish | after a dodge, blows land lighter |
| Still + Sink | Spider | held foes stay slowed |
| Still + Hunger | Heron | hitting held foes heals |
| Still + Flee | Deer | stand still, and the next dodge goes further |
| Sink + Hunger | Leech | hitting slowed foes heals |
| Sink + Flee | Eel | dodge again sooner |
| Hunger + Flee | Crow | dodge past a wounded foe to drink from it |

  - Wolf (Rend + Hunger), Bear (Break + Hunger) and Wasp (Sting + Flee) match the kind names of rounds 3 and 21. Round 21's "hare = Flee + Watch" doesn't clash: Watch isn't built.
- **Compatibility is a fact about the two souls, not chance or will** (round 15). Example: killer and killed cannot share a stone.
- **Three gates, in order** (round 15; only the first is built):
  1. **Type:** two different root names (built).
  2. **Compatibility** (every fuse): decides whether the fuse holds or fails. Fail: the stones break, souls go loose, corruption rises.
  3. **Consent** (only willing + willing): decides whether the result is willing (bare, no corruption) or forced (wired, downside, corruption). Forced souls have no consent to give.
  - **Each layer has its own message.** Proposed: incompatible, "These two cannot share a stone." / refused, "Neither will have the other."
- **Compatibility can be known only after reading both runes.** Until then a fuse is a gamble. (round 9)
- **An incompatible fuse fails and adds corruption.** (round 9) Reading taken: the broken stones let their souls loose.
- **Fusing a willing rune** (round 14): the result stays willing only if both are willing and the two souls consent. If they refuse and he fuses anyway, the result is forced: wired, with a downside. Willing + forced always gives forced.
- **A refused fuse is wired by the Wanderer himself,** with iron scrap from his bag (e.g. Rusted Blade, Cracked Plate). He is the jailer in the plainest way. (round 15)
- **Corruption on a fuse that holds:** only if the result is forced. (round 14)
- Costs shards (round 3). Round 3's phrases ("the cut that feeds", "the edge that holds", "the shell that feeds") are older flavour; the kind name now names the stone.
- *Gap:* in game any two different single runes fuse if you have the shards. Not built: compatibility, failure, consent, willing/forced state, family downsides, reading, scrap cost, corruption.

## Open

- **Flagged by round 42, not settled:**
  - **Kind names already mean beasts.** Round 3 says every wolf shares one name (Rend and Hunger), and round 34 makes beast stones real ("Ox-stone, from a yoke"). Is a Rune of the Wolf two men who together spell "wolf", or does it hold something of a wolf? A player will ask why two dead soldiers make a wolf, and how it differs from a true beast stone (always Pale, round 34).
  - **Plants and a tree among the kinds** (Bramble, Sundew, Oak). Round 21 allowed plants for root names (nettle for Sting); does a name of kind cover things without a soul?
  - **75% each** is a game number; does the lore want a reason (two souls crowd one stone)?
  - **Kinds overlap the built resonances:** Beetle and Leech-shell have the same trait (overhealing becomes a shield); Wolf is close to Bloodletting, Ox to Bulwark; "Leech" is both a kind and part of a resonance name.
  - **The trait comes from the pair, not the men,** while compatibility is a fact about the men (round 15). Fine as long as compatibility only says yes or no.
- **Failed fuse as a trap-to-free path** (ranked open thread A). Leading proposal **A1:** both cracked stones survive, can be rebuilt and bound back with the two names he read, then freed; always costs more than never failing; a willing soul bound back comes back forced (binding is trapping). Others: A2 the names tear (he keeps only part of each); A3 one soul loosed, one burned; A4 both souls loosed into one Hollow.
  - From canon: a forced rune at a shrine has its soul freed and corruption drops, as for any rune; the wire doesn't matter to the good gods. Under A1 "comes back forced" is felt only if he uses it before freeing.
  - Under A1 he would bind a soul back into its own cracked stone; round 5 says "bind *someone else's* name". Proposal: read it as "a name you supply".
- Whether a failed fuse always breaks both stones, and whether its corruption scales with tier.
- **Does freeing a fused rune free both souls?**
- **Other incompatibilities** beyond killer and killed (kin? same company? two who died at the same rite?).

## Rejected

- **An incompatible fuse as "something worse"** than a failure (round 8). Narrowed round 9.
- **Every fuse that holds adds corruption** (round 13 reading). Rejected round 14.
- **A fused willing rune stays willing whatever its partner** (round 8 implication). Rejected round 14.

## Related

[Rune types](rune-types.md) · [Crimson](crimson.md) · [Root names](root-names.md) · [What runes are](what-runes-are.md) · [Willing and forced](willing-and-forced.md)
