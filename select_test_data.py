#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import codecs
import re

UTF8Reader = codecs.getreader('utf8')
sys.stdin = UTF8Reader(sys.stdin)
UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)
sys.stderr = UTF8Writer(sys.stderr)

MAX_PER_CRITERION = 3

final_muids = list()

# no creture type - "Nameless Race"

def listify(withcommas):
    result = list()
    step1 = withcommas.split(",")
    for val in step1:
        step2 = val.lower().strip()
        result.append(step2)
    return result


symbols_list = ['{c}', '{t}', '{e}', '{q}', '{w}', '{u}', '{b}', '{r}', '{g}', '{s}', '{x}', "{wp}","{up}","{bp}","{rp}","{gp}","{2w}","{2u}","{2b}","{2r}","{2g}","{wu}","{wb}","{ub}","{ur}","{br}","{bg}","{rg}","{rw}","{gw}","{gu}","{w/p}","{u/p}","{b/p}","{r/p}","{g/p}","{2/w}","{2/u}","{2/b}","{2/r}","{2/g}","{w/u}","{w/b}","{u/b}","{u/r}","{b/r}","{b/g}","{r/g}","{r/w}","{g/w}","{g/u}"]
for i in range (0,22):
    symbols_list.append("{" + str(i) + "}")
    
power_list = list()
for i in range(0,21):
    power_list.append(str(i))
power_list.append("*")
power_list.append("1+*")

toughness_list = list(power_list)

supertypes_list = listify("Basic, Legendary, Ongoing, Snow, World")

types_list = listify("artifact, conspiracy, creature, enchantment, instant, land, phenomenon, plane, planeswalker, scheme, sorcery, tribal, vanguard")

subtypes = "Advisor, Aetherborn, Ally, Angel, Antelope, Ape, Archer, Archon, Artificer, Assassin, Assembly-Worker, Atog, Aurochs, Avatar, Badger, Barbarian, Basilisk, Bat, Bear, Beast, Beeble, Berserker, Bird, Blinkmoth, Boar, Bringer, Brushwagg, Camarid, Camel, Caribou, Carrier, Cat, Centaur, Cephalid, Chimera, Citizen, Cleric, Cockatrice, Construct, Coward, Crab, Crocodile, Cyclops, Dauthi, Demon, Deserter, Devil, Dinosaur, Djinn, Dragon, Drake, Dreadnought, Drone, Druid, Dryad, Dwarf, Efreet, Elder, Eldrazi, Elemental, Elephant, Elf, Elk, Eye, Faerie, Ferret, Fish, Flagbearer, Fox, Frog, Fungus, Gargoyle, Germ, Giant, Gnome, Goat, Goblin, God, Golem, Gorgon, Graveborn, Gremlin, Griffin, Hag, Harpy, Hellion, Hippo, Hippogriff, Homarid, Homunculus, Horror, Horse, Hound, Human, Hydra, Hyena, Illusion, Imp, Incarnation, Insect, Jackal, Jellyfish, Juggernaut, Kavu, Kirin, Kithkin, Knight, Kobold, Kor, Kraken, Lamia, Lammasu, Leech, Leviathan, Lhurgoyf, Licid, Lizard, Manticore, Masticore, Mercenary, Merfolk, Metathran, Minion, Minotaur, Mole, Monger, Mongoose, Monk, Monkey, Moonfolk, Mutant, Myr, Mystic, Naga, Nautilus, Nephilim, Nightmare, Nightstalker, Ninja, Noggle, Nomad, Nymph, Octopus, Ogre, Ooze, Orb, Orc, Orgg, Ouphe, Ox, Oyster, Pegasus, Pentavite, Pest, Phelddagrif, Phoenix, Pilot, Pincher, Pirate, Plant, Praetor, Prism, Processor, Rabbit, Rat, Rebel, Reflection, Rhino, Rigger, Rogue, Sable, Salamander, Samurai, Sand, Saproling, Satyr, Scarecrow, Scion, Scorpion, Scout, Serf, Serpent, Servo, Shade, Shaman, Shapeshifter, Sheep, Siren, Skeleton, Slith, Sliver, Slug, Snake, Soldier, Soltari, Spawn, Specter, Spellshaper, Sphinx, Spider, Spike, Spirit, Splinter, Sponge, Squid, Squirrel, Starfish, Surrakar, Survivor, Tetravite, Thalakos, Thopter, Thrull, Treefolk, Trilobite, Triskelavite, Troll, Turtle, Unicorn, Vampire, Vedalken, Viashino, Volver, Wall, Warrior, Weird, Werewolf, Whale, Wizard, Wolf, Wolverine, Wombat, Worm, Wraith, Wurm, Yeti, Zombie, Zubera"
subtypes = subtypes + "," + "Clue, Contraption, Equipment, Fortification, Treasure, Vehicle"
subtypes = subtypes + "," + "Aura, Cartouche, Curse, Shrine"
subtypes = subtypes + "," + "Desert, Forest, Gate, Island, Lair, Locus, Mine, Mountain, Plains, Power-Plant, Swamp, Tower, Urza's"
subtypes = subtypes + "," + "Ajani, Arlinn, Ashiok, Bolas, Chandra, Dack, Daretti, Domri, Dovin, Elspeth, Freyalise, Garruk, Gideon, Huatli, Jace, Karn, Kaya, Kiora, Koth, Liliana, Nahiri, Narset, Nissa, Nixilis, Ral, Saheeli, Samut, Sarkhan, Sorin, Tamiyo, Teferi, Tezzeret, Tibalt, Ugin, Venser, Vraska, Xenagos"
subtypes = subtypes + "," + "Arcane, Trap"
subtypes = subtypes + "," + "Alara, Arkhos, Azgol, Belenon, Bolas's Meditation Realm, Dominaria, Equilor, Ergamon, Fabacin, Innistrad, Iquatana, Ir, Kaldheim, Kamigawa, Karsus, Kephalai, Kinshala, Kolbahan, Kyneth, Lorwyn, Luvion, Mercadia, Mirrodin, Moag, Mongseng, Muraganda, New Phyrexia, Phyrexia, Pyrulea, Rabiah, Rath, Ravnica, Regatha, Segovia, Serra's Realm, Shadowmoor, Shandalar, Ulgrotha, Valla, Vryn, Wildfire, Xerex, and Zendikar"
subtypes_list = listify(subtypes)


keyword_abilities = "Deathtouch, Defender, Double Strike, Enchant, Equip, First Strike, Flash, Flying, Haste, Hexproof, Indestructible, Intimidate, Landwalk, Lifelink, Protection, Reach, Shroud, Trample, Vigilance, Banding, Rampage, Cumulative Upkeep, Flanking, Phasing, Buyback, Shadow, Cycling, Echo, Horsemanship, Fading, Kicker, Flashback, Madness, Fear, Morph, Amplify, Provoke, Storm, Affinity, Entwine, Modular, Sunburst, Bushido, Soulshift, Splice, Offering, Ninjutsu, Epic, Convoke, Dredge, Transmute, Bloodthirst, Haunt, Replicate, Forecast, Graft, Recover, Ripple, Split Second, Suspend, Vanishing, Absorb, Aura Swap, Delve, Fortify, Frenzy, Gravestorm, Poisonous, Transfigure, Champion, Changeling, Evoke, Hideaway, Prowl, Reinforce, Conspire, Persist, Wither, Retrace, Devour, Exalted, Unearth, Cascade, Annihilator, Level Up, Rebound, Totem Armor, Infect, Battle Cry, Living Weapon, Undying, Miracle, Soulbond, Overload, Scavenge, Unleash, Cipher, Evolve, Extort, Fuse, Bestow, Tribute, Dethrone, Hidden Agenda, Outlast, Prowess, Dash, Exploit, Menace, Renown, Awaken, Devoid, Ingest, Myriad, Surge, Skulk, Emerge, Escalate, Melee, Crew, Fabricate, Partner, Undaunted, Improvise, Aftermath, Embalm, Eternalize, Afflict"

keyword_actions = "Activate, Attach, Cast, Counter, Create, Destroy, Discard, Exchange, Exile, Fight, Play, Regenerate, Reveal, Sacrifice, Scry, Search, Shuffle, Tap and Untap, Fateseal, Clash, Planeswalk, Set in Motion, Abandon, Proliferate, Transform, Detain, Populate, Monstrosity, Vote, Bolster, Manifest, Support, Investigate, Meld, Goad, Exert, Explore"

ability_words = "Battalion,Bloodrush,Channel,Chroma,Cohort,Constellation,Converge,Council's dilemma,Delirium,Domain,Eminence,Enrage,Fateful hour,Ferocious,Formidable,Grandeur,Hellbent,Heroic,Imprint,Inspired,Join forces,Kinship,Landfall,Lieutenant,Metalcraft,Morbid,Parley,Radiance,Raid,Rally,Revolt,Spell mastery,Strive,Sweep,Tempting offer,Threshold,Will of the council"

keywords_list = listify(keyword_abilities)
keywords_list.extend(listify(keyword_actions))
keywords_list.extend(listify(ability_words))

keywords_list.extend(symbols_list)

# Note that cards with non-normal layout will have multiple cards in the json, but they will have the same multiverseid. That means we don't have to go and find matches.
### REVISIT - double-check meld!
layouts = "normal, split, flip, double-faced, token, plane, scheme, phenomenon, leveler, vanguard, meld"
layout_list = listify(layouts)

loadeddata = json.load(sys.stdin)

# test to see if this is a set, or if it is a set of sets.
data = {"cards": []}
if "name" not in loadeddata:
    # must be a set of sets - a dictionary. let's iterate through each set within this dictionary, looking for sets...
    for mtgset in loadeddata:
        nl = loadeddata[mtgset]
        if "name" in nl and "cards" in nl:
            #print "adding " + str(len(nl["cards"])) + " cards from " + nl["name"]
            data["cards"].extend(nl["cards"])
else:
    data = loadeddata

final_muids = list()
final_muids.append(262875) # Huntmaster of the Fells
final_muids.append(262699) # Ravager of the Fells
final_muids.append(368950) # Wear/Tear

# used for finding mciNumbers with letters
mciNum_re = re.compile('^([0-9]+)([a-d])+$')

def add_card(cards_list, card_dict, allcards_list):
    if "multiverseid" in card_dict:
        cards_list.append(card_dict["multiverseid"])
        # going to use the mciNumber to see if there is a related card...
        if "mciNumber" in card_dict:
            mat = mciNum_re.match(card_dict["mciNumber"])
            if mat:
                #sys.stderr.write("Looking because of " + card_dict["mciNumber"] + "\n")
                # hunt down the siblings...
                for hcard in allcards_list:
                    #sys.stderr.write("L102\n")
                    # only look at cards that are near us, because the mciNumber is relative to our set.
                    if "multiverseid" in hcard and int(hcard["multiverseid"]) > int(card_dict["multiverseid"]) - 300  and int(hcard["multiverseid"]) < int(card_dict["multiverseid"]) + 300:
                        #sys.stderr.write("L105\n")
                        if "mciNumber" in hcard and hcard["mciNumber"] is not card_dict["mciNumber"]:
                            #sys.stderr.write("L107\n")
                            for letter in ['a','b','c','d']:
                                #sys.stderr.write("L109 - " + str(hcard["mciNumber"]) + " == " + str(mat.group(1)) + letter + "\n")
                                if str(hcard["mciNumber"]) == str(mat.group(1)) + letter:
                                    cards_list.append(hcard["multiverseid"])
                                    #sys.stderr.write("MATCH!!! Adding " + str(hcard["multiverseid"]) + " because of " + str(card_dict["multiverseid"]) + "!!\n")
        return 1
    else:
        #sys.stderr.write("==========\nCard missing multiverseid\n" + json.dumps(card_dict, indent=2) + "\n")
        return 0


# cards with fun things in their names
spec_chars = [u'Æ', u'æ', '0', ',', '-', '_', '!', 'Ae']
for spec_char in spec_chars:
    found = 0
    for card in data["cards"]:
        if "name" in card and card["name"].find(spec_char) > -1:
            if found >= MAX_PER_CRITERION:
                continue
            sys.stderr.write(card["name"] + "\n")
            found = found + add_card(final_muids, card, data["cards"])


# each supertype
for ctype in supertypes_list:
    found = 0
    for card in data["cards"]:
        if found >= MAX_PER_CRITERION:
            continue
        if "supertypes" in card:
            if card["supertypes"][0].lower() == ctype:
                found = found + add_card(final_muids, card, data["cards"])

                
# each card type
for ctype in types_list:
    found = 0
    for card in data["cards"]:
        if found >= MAX_PER_CRITERION:
            continue
        if "types" in card:
            if card["types"][0].lower() == ctype.lower():
                found = found + add_card(final_muids, card, data["cards"])


# legendary for each type
for ctype in types_list:
    found = 0
    for card in data["cards"]:
        if "supertypes" in card and card["supertypes"][0].lower() == "legendary":
            if found >= MAX_PER_CRITERION:
                continue
            if "types" in card:
                if card["types"][0].lower() == ctype.lower():
                    found = found + add_card(final_muids, card, data["cards"])


# cards with multiple types
for counter in range(0, 4):
    found = 0
    for card in data["cards"]:
        if found >= MAX_PER_CRITERION:
            continue
        if counter == 0:
            if "types" not in card:
                found = found + add_card(final_muids, card, data["cards"])
        else:
            if "types" in card and len(card["types"]) == counter:
                found = found + add_card(final_muids, card, data["cards"])


# cards with multiple subtypes
for counter in range(0, 4):
    found = 0
    for card in data["cards"]:
        if found >= MAX_PER_CRITERION:
            continue
        if counter == 0:
            if "subtypes" not in card:
                found = found + add_card(final_muids, card, data["cards"])
        else:
            if "subtypes" in card and len(card["subtypes"]) == counter:
                found = found + add_card(final_muids, card, data["cards"])


# each card subtype
for ctype in subtypes_list:
    found = 0
    for card in data["cards"]:
        if found >= MAX_PER_CRITERION:
            continue
        if "subtypes" in card:
            for counter in range(len(card["subtypes"])):
                if card["subtypes"][counter].lower() == ctype.lower():
                    found = found + add_card(final_muids, card, data["cards"])


# cards by power
for cpower in power_list:
    found = 0
    for card in data["cards"]:
        if "power" in card and card["power"] == cpower:
            if found >= MAX_PER_CRITERION:
                continue
            found = found + add_card(final_muids, card, data["cards"])

            
# cards by toughness
for ctoughness in toughness_list:
    found = 0
    for card in data["cards"]:
        if "toughness" in card and card["toughness"] == ctoughness:
            if found >= MAX_PER_CRITERION:
                continue
            found = found + add_card(final_muids, card, data["cards"])


# cards with no rules
found = 0
for card in data["cards"]:
    if "text" not in card or len(card["text"]) == 0:
        if found >= MAX_PER_CRITERION:
            continue
        found = found + add_card(final_muids, card, data["cards"])


# cards with keywords
for word in keywords_list:
    found = 0
    for card in data["cards"]:
        if found >= MAX_PER_CRITERION:
            continue
        if "text" in card:
            #print card["text"].lower()
            if card["text"].lower().find(word) >= 0:
                found = found + add_card(final_muids, card, data["cards"])


# layouts
for layout in layout_list:
    found = 0
    for card in data["cards"]:
        if found >= MAX_PER_CRITERION:
            continue
        if "layout" in card:
            if card["layout"].lower() == layout:
                found = found + add_card(final_muids, card, data["cards"])


# cards by mana symbols in cost
for symbol in symbols_list:
    found = 0
    for card in data["cards"]:
        if found >= MAX_PER_CRITERION:
            continue
        if "manaCost" in card:
            if card["manaCost"].lower().find(symbol) >= 0:
                #print card["name"] + " - " + card["manaCost"]
                found = found + add_card(final_muids, card, data["cards"])


# cards by cmc
for cmc in range (0,22):
    found = 0
    for card in data["cards"]:
        if "cmc" in card and card["cmc"] == cmc:
            if found >= MAX_PER_CRITERION:
                continue
            #print card["name"] + " - " + str(card["cmc"])
            found = found + add_card(final_muids, card, data["cards"])


output = {}
output["name"] = "MTG Test Data"
output["code"] = "CNTest"
output["cards"] = list()

for card in data["cards"]:
    if "multiverseid" in card and card["multiverseid"] in final_muids:
        #print card["name"]
        output["cards"].append(card)
#    if card["name"] == "Alive":
#        print json.dumps(card, indent=2)
print json.dumps(output, indent=2)
