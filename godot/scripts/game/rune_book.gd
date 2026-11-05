class_name RuneBook

# Every rune number lives here, so playtesting tunes this file only (lore: lore/Runes/rune-types.md).
# Three families, one per Quiet god; each subtype is a soul's strongest verb at death. Two souls at
# most share a stone, and Crimson never fuses. Per-tier lists run Pale to Crimson.

# Order of the icon rows (art/drafts/ui/icons.py ORDER) and of a fused key's two halves.
const ORDER := ["rend", "break", "sting", "ward", "still", "sink", "hunger", "flee"]

# Folk grade shown until the Wanderer learns which god is behind it.
const FAMILIES := {
	"grudge": {"grade": "Biter", "god": "Grudge"},
	"mortmain": {"grade": "Holder", "god": "Mortmain"},
	"hush": {"grade": "Taker", "god": "Hush"},
}

# Value per tier is a percent, except Still's (hundredths of a second). text gets the value.
const SUBTYPES := {
	"rend": {"family": "grudge", "part": "blade", "desc": "Sharpens the edge.",
		"tiers": [5, 9, 14, 20, 28, 40], "text": "+%d%% damage"},
	"break": {"family": "grudge", "part": "blade", "desc": "Breaks what it strikes.",
		"tiers": [12, 16, 21, 27, 34, 45], "text": "+%d%% break per hit"},
	"sting": {"family": "grudge", "part": "armor", "desc": "Hurts what touches it.",
		"tiers": [10, 15, 22, 30, 40, 55], "text": "%d%% of blows hurt back"},
	"ward": {"family": "mortmain", "part": "armor", "desc": "Hardens the flesh.",
		"tiers": [4, 7, 11, 16, 22, 30], "text": "-%d%% damage taken"},
	"still": {"family": "mortmain", "part": "blade", "desc": "Holds what it strikes.",
		"tiers": [15, 22, 30, 40, 52, 70], "text": "Struck foes held %.2fs"},
	"sink": {"family": "mortmain", "part": "blade", "desc": "Drags down what it strikes.",
		"tiers": [15, 20, 26, 33, 40, 50], "text": "Struck foes %d%% slower"},
	"hunger": {"family": "hush", "part": "blade", "desc": "Drinks from the wounded.",
		"tiers": [2, 3, 5, 7, 10, 15], "text": "%d%% of damage dealt heals you"},
	"flee": {"family": "hush", "part": "armor", "desc": "Runs from death.",
		"tiers": [8, 12, 17, 23, 30, 40], "text": "+%d%% dodge and run"},
}
const SINK_TIME := 2.0
const BREAK_FULL := 100.0
# Each half of a fused rune works at this share of a single rune.
const FUSED_SHARE := 0.75
const NOTCH_BONUS := 0.2
const MAX_NOTCHES := 5
# Mortmain's grip (lore: Willing and forced): every forced rune pays a cost on the shadow of its verb,
# growing with tier more slowly than the gift (Pale to Gold; Crimson's burden is the prisoner's
# instead). Rend's is health per kill; the rest are percents.
const GRIPS := {
	"rend": {"tiers": [1, 2, 3, 4, 5], "text": "Each kill costs %d health"},
	"break": {"tiers": [2, 3, 4, 5, 6], "text": "Blows on you land %d%% harder"},
	"sting": {"tiers": [10, 15, 20, 25, 30], "text": "Hurting back costs you %d%% of it"},
	"ward": {"tiers": [2, 3, 4, 5, 6], "text": "%d%% slower"},
	"still": {"tiers": [5, 8, 11, 14, 18], "text": "Dodge recovers %d%% slower"},
	"sink": {"tiers": [3, 5, 7, 9, 11], "text": "Dodges %d%% shorter"},
	"hunger": {"tiers": [10, 15, 20, 25, 30], "text": "Other healing %d%% weaker"},
	"flee": {"tiers": [2, 3, 4, 6, 8], "text": "Your hits %d%% weaker"},
}
# Reading (lore: Reading and echoes): a lashed rune works at UNREAD_POWER until its verb has been done
# READ_USES times for its tier; then it gives full power and its soul's echo (echoes.json).
const UNREAD_POWER := 0.5
const READ_USES := [15, 25, 35, 45, 60, 80]
# Corruption a soul bound into an empty stone adds (Runes.bind): binding is trapping.
const BIND_CORRUPTION := 0.03
# The rites (lore: The six rites), by tier: a dark rite adds corruption, freeing at Wend's road takes
# it away. Crimson has no rite yet (its Release frees a jailer and a prisoner).
const DARK_RITE_CORRUPTION := [0.04, 0.05, 0.06, 0.08, 0.10]
const FREE_CORRUPTION := [0.02, 0.03, 0.04, 0.05, 0.07]
# Health a good rite costs at the Pull.
const KNEEL_BLOOD := 20.0
# What a common soul needs finished before Wend's road, drawn from its id: nameless, unforgiven, ready.
const NEEDS := [["name"], ["fire"], []]
const NEED_TEXT := {"name": "He has lost his name.", "fire": "He holds onto something.", "road": "He is ready for the road."}
# Uttering (lore: Uttering): a lashed rune's soul burns as one spell, Pale to Gold (Crimson's is its
# own thing, not built). Values scale like a passive: notches, fused share, unread power. radius: px
# around him. Speaking adds corruption and gives shards back (a
# Pale stone crumbles to dust); a hatred Hollow rises, stronger by tier. At the Pull spells are
# PULL_POWER stronger and cost no corruption.
const SPELLS := {
	"rend": {"tiers": [30, 45, 65, 90, 120], "radius": 130.0, "text": "A scythe of blood through all near for %d"},
	"break": {"tiers": [15, 22, 30, 40, 55], "radius": 110.0, "text": "Knocks down all near for %d"},
	"sting": {"tiers": [20, 30, 42, 58, 80], "radius": 120.0, "text": "Splinters all near for %d, bleeding"},
	"ward": {"tiers": [25, 35, 50, 70, 95], "radius": 0.0, "text": "A shell of %d health"},
	"still": {"tiers": [1.5, 2.0, 2.5, 3.0, 4.0], "radius": 150.0, "text": "Holds all near for %.1fs"},
	"sink": {"tiers": [3.0, 4.0, 5.0, 6.0, 8.0], "radius": 150.0, "text": "Drags all near down for %.1fs"},
	"hunger": {"tiers": [10, 15, 22, 30, 40], "radius": 120.0, "text": "Drinks %d from each near"},
	"flee": {"tiers": [1.0, 1.4, 1.8, 2.2, 3.0], "radius": 0.0, "text": "Untouchable for %.1fs"},
}
const SINK_SPELL_SLOW := 0.6
const UTTER_CORRUPTION := [0.02, 0.03, 0.04, 0.05, 0.06]
const UTTER_SHARDS := [0, 3, 5, 8, 12]
const PULL_POWER := 1.5
# A hatred Hollow's health and blow, as multiples of a Hollow's, by the uttered stone's tier.
const HATRED_HP := [1.0, 1.5, 2.2, 3.0, 4.0]
const HATRED_DAMAGE := [1.0, 1.2, 1.4, 1.7, 2.0]
const HATRED_RISE_DISTANCE := 90.0
const CARVE_COST := [3, 6, 10, 15, 21]
const FUSE_COST_PER_TIER := 5

# A fused rune's kind trait. when: the moment it fires; if: what must be true then; do: the effect.
# Amounts are the Azure baseline, scaled by KIND_POWER for the stone's tier and by its notches.
#   when  strike (each hit), finisher (last combo hit), hurt (a blow lands on you), dodge (you start
#         one), through (a dodge passes a foe), broken (Break knocks a foe down), held (you hold a
#         foe), reflect (Sting hurts back), heal_over (healing past full), always
#   if    bleeding / held / slowed (the foe), attacking / still (you), wounded (the foe is hurt)
#   do    heal, bleed, damage (this hit, %), empower (next hit, %), hold, slow, knockdown, break,
#         hurt (the foe), guard (% less damage; for `time` or while the `if` holds), shield,
#         steady (no knockback), reflect (+%), dodge (+% next dodge), quick (% shorter dodge cooldown)
const KIND_POWER := [0.8, 1.0, 1.2, 1.4, 1.7]
const STILL_AFTER := 0.5
const KINDS := {
	"rend-break": {"name": "Wolverine", "when": "finisher", "do": "bleed", "dps": 4.0, "time": 3.0, "desc": "The last blow of a combo bleeds."},
	"rend-sting": {"name": "Bramble", "when": "hurt", "do": "bleed", "dps": 3.0, "time": 3.0, "desc": "What strikes you bleeds."},
	"rend-ward": {"name": "Boar", "when": "hurt", "do": "empower", "amount": 50.0, "desc": "Take a blow, and your next hit is stronger."},
	"rend-still": {"name": "Mantis", "when": "strike", "if": "held", "do": "damage", "amount": 40.0, "desc": "Held foes take more damage."},
	"rend-sink": {"name": "Pike", "when": "strike", "if": "slowed", "do": "bleed", "dps": 2.0, "time": 2.0, "desc": "Slowed foes bleed."},
	"rend-hunger": {"name": "Wolf", "when": "strike", "if": "bleeding", "do": "heal", "amount": 2.0, "desc": "Hitting the bleeding heals you."},
	"rend-flee": {"name": "Hawk", "when": "dodge", "do": "empower", "amount": 40.0, "desc": "Your first hit after a dodge is stronger."},
	"break-sting": {"name": "Ram", "when": "hurt", "if": "attacking", "do": "knockdown", "desc": "Strike you mid-swing and be thrown down."},
	"break-ward": {"name": "Ox", "when": "always", "do": "steady", "desc": "Blows can't shove you."},
	"break-still": {"name": "Badger", "when": "strike", "if": "held", "do": "break", "amount": 25.0, "desc": "Held foes break faster."},
	"break-sink": {"name": "Elk", "when": "strike", "if": "slowed", "do": "knockdown", "desc": "Slowed foes are thrown down."},
	"break-hunger": {"name": "Bear", "when": "broken", "do": "heal", "amount": 6.0, "desc": "Breaking a foe heals you."},
	"break-flee": {"name": "Horse", "when": "through", "do": "hold", "time": 0.5, "desc": "Dodge through a foe to stagger it."},
	"sting-ward": {"name": "Crab", "when": "always", "do": "reflect", "amount": 20.0, "desc": "Blows hurt back harder."},
	"sting-still": {"name": "Scorpion", "when": "hurt", "do": "hold", "time": 0.8, "desc": "What strikes you is held."},
	"sting-sink": {"name": "Sundew", "when": "hurt", "do": "slow", "amount": 40.0, "time": 2.5, "desc": "What strikes you is slowed."},
	"sting-hunger": {"name": "Tick", "when": "reflect", "do": "heal", "amount": 50.0, "desc": "Hurting back heals you (% of it)."},
	"sting-flee": {"name": "Wasp", "when": "through", "do": "hurt", "amount": 6.0, "desc": "Dodge through a foe to hurt it."},
	"ward-still": {"name": "Oak", "when": "always", "if": "still", "do": "guard", "amount": 25.0, "desc": "Standing still hardens you."},
	"ward-sink": {"name": "Toad", "when": "hurt", "if": "slowed", "do": "guard", "amount": 30.0, "desc": "Slowed foes hit you softer."},
	"ward-hunger": {"name": "Beetle", "when": "heal_over", "do": "shield", "amount": 20.0, "desc": "Healing past full becomes a shield."},
	"ward-flee": {"name": "Crayfish", "when": "dodge", "do": "guard", "amount": 30.0, "time": 1.5, "desc": "After a dodge, blows land lighter."},
	"still-sink": {"name": "Spider", "when": "held", "do": "slow", "amount": 30.0, "time": 2.0, "desc": "Held foes stay slowed after."},
	"still-hunger": {"name": "Heron", "when": "strike", "if": "held", "do": "heal", "amount": 3.0, "desc": "Hitting held foes heals you."},
	"still-flee": {"name": "Deer", "when": "always", "if": "still", "do": "dodge", "amount": 30.0, "desc": "Stand still, and your next dodge goes further."},
	"sink-hunger": {"name": "Leech", "when": "strike", "if": "slowed", "do": "heal", "amount": 2.0, "desc": "Hitting slowed foes heals you."},
	"sink-flee": {"name": "Eel", "when": "always", "do": "quick", "amount": 35.0, "desc": "You dodge again sooner."},
	"hunger-flee": {"name": "Crow", "when": "through", "if": "wounded", "do": "heal", "amount": 4.0, "desc": "Dodge past a wounded foe to drink from it."},
}

# Crimson: the prisoner's burden on the soul's verb.
const CRIMSON := 6
const CRIMSON_HURT := 3.0
const CRIMSON_STARVE := 0.5
const CRIMSON_SLOW := 0.85
const CURSED_DAMAGE_TAKEN := 1.1
const CRIMSON_TEXT := {
	"rend": "Every blow on you hurts %d more" % CRIMSON_HURT,
	"hunger": "You starve out of a fight",
	"ward": "%d%% slower" % roundi((1 - CRIMSON_SLOW) * 100),
}

# Resonances: sets of verbs lashed in one part (a fused rune counts as both of its verbs).
const RESONANCES := [
	{"name": "Flay", "part": "blade", "needs": {"rend": 3}, "desc": "Every third hit opens a bleed."},
	{"name": "Gorge", "part": "blade", "needs": {"hunger": 3}, "desc": "Killing blows heal."},
	{"name": "Bloodletting", "part": "blade", "needs": {"rend": 1, "hunger": 1}, "desc": "Every third hit bleeds. Hitting the bleeding heals."},
	{"name": "Riposte", "part": "blade", "needs": {"rend": 1, "ward": 1}, "desc": "Dodge a blow and your next strike deals double."},
	{"name": "Leech-shell", "part": "blade", "needs": {"hunger": 1, "ward": 1}, "desc": "Overhealing becomes a shield."},
	{"name": "Bulwark", "part": "armor", "needs": {"ward": 2}, "desc": "Blows shove you no more and lose some force."},
	{"name": "Scab", "part": "armor", "needs": {"ward": 1, "hunger": 1}, "desc": "Out of the fight, wounds close."},
]
const BLEED := {"every": 3, "dps": 4.0, "time": 3.0, "light_dps": 2.0, "light_time": 2.0}
const GORGE_HEAL := 0.1
const BLOODLET_HEAL := 2.0
const SHIELD_MAX := 20.0
const BULWARK_BLOCK := 5.0
const SCAB := {"after": 3.0, "regen": 1.0}
