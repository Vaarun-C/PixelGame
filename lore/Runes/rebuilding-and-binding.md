# Rebuilding and Binding

When a rune is shattered, a village carver can patch it with mortar. It comes back one tier lower and empty. The Wanderer can then put a soul into it by calling that soul's name: binding. Binding is trapping, so it costs corruption, but it is also how he catches loose souls to free them.

## Canon

### Rebuilding (design canon, not built)

- **Only in a village, never in the field.** The carver is the village monk, paid in **metal by weight**. (round 5)
- **The carver only patches the shattered rune: he fills the cracks with mortar** (round 37). It can't be fully repaired, which is why it drops a tier. **The blank (Mortmain's work) is still the stone underneath.** Proposed carver line: "That's the most I can do."
- The rune comes back **one tier lower**. **The cracked stone caps the tier:** at most one tier below what it was, lower if a weaker name is bound. (round 5)
- **The rebuilt stone is empty** until you bind a true name into it. (round 5)
- **Uttering a Pale rune crumbles it to dust,** and the name in it is forgotten for good. **Pale runes can't be rebuilt.** (round 5; since round 7 every utterance destroys the soul, so Pale differs only in leaving no stone)
- **Rebuilding raises corruption.** (rounds 6–9)

### Binding (rounds 5, 13, 21)

- **Binding sources** (round 5):
  - (a) **Names of the dead, given by the living** (kin, friends).
  - (b) **True names of noted beings the Wanderer has defeated** (bosses, Hollows of note).
  - (c) **Rarely, a living volunteer.** They go hollow.
  - (d) **A living person without consent, only through the [living binding](../Mechanics/the-living-binding.md), a dark rite** (round 21). They go hollow too.
- **Binding at the body** (round 49, the user): at a laid-down Hollow, before it rises, the Wanderer traps its soul in a **blank**. The body gives a breath while it still holds a soul. Result: an **unread forced stone.** It **costs corruption and uses up a blank.** Killing and burning cost none; binding is the only one of the three that does. Then the stone is freed like any other: read it by fighting with it, then do its rites at a village from the step it missed (nameless: ledger, then road; unforgiven: fire, then road; ready: road). Or use it: fight with it, or utter it (burns the soul, raises a hatred Hollow). (seen in: godot/scripts/game/rites.gd needs)
- **True blanks are not the same as mortar-patched stones** (round 49b, the user). The Wanderer buys true blanks at the **chapel each village holds, where the village monk lives.** What each can do: proposal in Open.
- **Binding calls a name, not a body** (round 13). A bound name pulls its soul from wherever it is, so he needs a dead man's name, not his Hollow. **Proposed reconciliation with round 49** (not settled): at the body the soul is present and needs no name; calling a name is for souls that have drifted away. Keep both.
- **The binding tells him where the soul is** (round 13):
  - **Loose:** the soul is caught in the stone, and somewhere a Hollow drops.
  - **"The name is held":** the soul is already in a stone (maybe in his own bag); the binding fails.
  - **Nothing answers:** the soul was burned or freed.
  - **Forgotten, even by kin:** the soul was offered.
- **Binding is trapping, so it adds corruption;** the soul is then freed by taking the stone to a wayside shrine (the round 9 trap-to-free path). Trapping feeds Mortmain (round 37).
- **Where names come from:** kin, and rarely a **rite cord** (knots = a number, looked up in a chapel ledger or with a monk). Dark monks lie about cords by swapping names. See [Hollows: loose souls](../Characters/hollows.md).

## Open

- **What can a true blank do in binding that a patched stone can't?** (open question, round 49b) [A true blank is whole: it takes a soul at the body (the breath) at the soul's own tier. A patched stone leaks through its mortar, so it binds only by name, where the name pulls the soul tight, one tier lower (round 5). Carver line: "Mortar holds a name. It won't hold a breath."]
- **Knock-ons of chapel blanks** (open questions, round 49b): (a) blanks are Mortmain's craft and only keepers make them (round 36), so who makes the village chapel's? [No one now: they are war stock the crowns paid for and never handed out, sold by an ordinary monk who believes the doctrine. The stock runs down, which keeps blanks scarce; a dark monk may make more in secret.] (b) Question 22 (the barterer's "empty stones" vs "No stones at my stall") is now answered: the monk sells them. (c) Is binding at the body the withholding rite (round 36)? Proposal: yes, the field form said over a man already down.
- **Who corrupts on rebuild.** The monk carves; the Wanderer binds. Proposal: binding is the trap; a dark carver could add more.
- **"Someone else's" name** (round 5) vs binding a soul back into its own stone under fuse option A1: read it as "a name you supply". See [Fusing](fusing.md).
- **How a villager's dead get named in conversation** (names must be exact game strings; persistence allows repeat visits; dialogue today is three fixed lines).
- **A village that loses a volunteer to hollowing.** Proposal (round 21): the same as a living-binding victim, a husk the kin feed until they burn it.
- **Carvers:** why they do it, and which carvers serve the dark gods. (round 5, open)

## Rejected

- **Rebuilt stone binds another soldier's splinters automatically; soldier freed only if you don't rebuild** (round 3 options a, c). Rejected round 4.
- **The living may be bound only as volunteers** (round 5 reading). Superseded round 21: without consent, only through the living binding.
