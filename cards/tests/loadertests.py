# -*- coding: utf-8 -*-
from django.test import TestCase, TransactionTestCase
from django_nose import FastFixtureTestCase
from cards.models import Color, Rarity, Type, Subtype, PhysicalCard, Card, BaseCard, CardRating, ExpansionSet, FormatBasecard, SearchPredicate
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.db import transaction
from cards.tests.helper import TestLoadHelper

from cards.management.commands.loadcardjson import Command
import sys
err = sys.stderr

class LoaderTestCase(TestCase):

    huntmaster_json = '''{"layout":"double-faced","type":"Creature — Human Werewolf","types":["Creature"],"colors":["Red","Green"],"multiverseid":262875,"names":["Huntmaster of the Fells","Ravager of the Fells"],"name":"Huntmaster of the Fells","subtypes":["Human","Werewolf"],"originalType":"Creature — Human Werewolf","cmc":4,"rarity":"Mythic Rare","artist":"Chris Rahn","power":"2","toughness":"2","manaCost":"{2}{R}{G}","text":"Whenever this creature enters the battlefield or transforms into Huntmaster of the Fells, put a 2/2 green Wolf creature token onto the battlefield and you gain 2 life.\\nAt the beginning of each upkeep, if no spells were cast last turn, transform Huntmaster of the Fells.","originalText":"Whenever this creature enters the battlefield or transforms into Huntmaster of the Fells, put a 2/2 green Wolf creature token onto the battlefield and you gain 2 life.\\nAt the beginning of each upkeep, if no spells were cast last turn, transform Huntmaster of the Fells.","number":"140a","imageName":"huntmaster of the fells","foreignNames":[{"language":"Chinese Traditional","name":"墮者獵師"},{"language":"Chinese Simplified","name":"堕者猎师"},{"language":"French","name":"Maître-chasseur de la lande"},{"language":"German","name":"Jagdmeister vom Kahlenberg"},{"language":"Italian","name":"Capocaccia delle Colline"},{"language":"Japanese","name":"高原の狩りの達人"},{"language":"Korean","name":"산지의 사냥꾼"},{"language":"Portuguese (Brazil)","name":"Mestre de Caça da Derrubada"},{"language":"Russian","name":"Ловчий Каменистых Холмов"},{"language":"Spanish","name":"Maestro de caza de las colinas"}],"legalities":{"Modern":"Legal","Innistrad Block":"Legal","Legacy":"Legal","Vintage":"Legal","Freeform":"Legal","Prismatic":"Legal","Tribal Wars Legacy":"Legal","Tribal Wars Standard":"Legal","Singleton 100":"Legal","Commander":"Legal"},"printings":["Dark Ascension"]}'''
    ravager_json = '''{"layout":"double-faced","type":"Creature — Werewolf","types":["Creature"],"colors":["Red","Green"],"multiverseid":262699,"names":["Huntmaster of the Fells","Ravager of the Fells"],"name":"Ravager of the Fells","subtypes":["Werewolf"],"originalType":"Creature — Werewolf","rarity":"Mythic Rare","artist":"Chris Rahn","power":"4","toughness":"4","text":"Trample\\nWhenever this creature transforms into Ravager of the Fells, it deals 2 damage to target opponent and 2 damage to up to one target creature that player controls.\\nAt the beginning of each upkeep, if a player cast two or more spells last turn, transform Ravager of the Fells.","originalText":"Trample\\nWhenever this creature transforms into Ravager of the Fells, it deals 2 damage to target opponent and 2 damage to up to one target creature that player controls.\\nAt the beginning of each upkeep, if a player cast two or more spells last turn, transform Ravager of the Fells.","number":"140b","imageName":"ravager of the fells","legalities":{"Modern":"Legal","Innistrad Block":"Legal","Legacy":"Legal","Vintage":"Legal","Freeform":"Legal","Prismatic":"Legal","Tribal Wars Legacy":"Legal","Tribal Wars Standard":"Legal","Singleton 100":"Legal","Commander":"Legal"},"printings":["Dark Ascension"]}'''

    magnivore_json = '''{"layout":"normal","type":"Creature — Lhurgoyf","types":["Creature"],"colors":["Red"],"multiverseid":83448,"name":"Magnivore","subtypes":["Lhurgoyf"],"originalType":"Creature — Lhurgoyf","cmc":4,"rarity":"Rare","artist":"Carl Critchlow","power":"*","toughness":"*","manaCost":"{2}{R}{R}","text":"Haste (This creature can attack the turn it comes under your control.)\\nMagnivore's power and toughness are each equal to the number of sorcery cards in all graveyards.","originalText":"Haste (This creature may attack the turn it comes under your control.)\\nMagnivore's power and toughness are each equal to the number of sorcery cards in all graveyards.","number":"202","imageName":"magnivore","foreignNames":[{"language":"Chinese Simplified","name":"噬咒兽"},{"language":"German","name":"Machtmampfer"},{"language":"Italian","name":"Magnivoro"},{"language":"Japanese","name":"猛烈に食うもの"},{"language":"Portuguese (Brazil)","name":"Magnívoro"},{"language":"Russian","name":"Магнивор"},{"language":"Spanish","name":"Magnívoro"}],"legalities":{"Modern":"Legal","Odyssey Block":"Legal","Legacy":"Legal","Vintage":"Legal","Freeform":"Legal","Prismatic":"Legal","Tribal Wars Legacy":"Legal","Singleton 100":"Legal","Commander":"Legal"},"printings":["Odyssey","Ninth Edition"]}'''

    colossus_sardia_json = '''{"layout":"normal","type":"Artifact Creature — Golem","types":["Artifact","Creature"],"multiverseid":1002,"name":"Colossus of Sardia","subtypes":["Golem"],"originalType":"Artifact Creature","cmc":9,"rarity":"Rare","artist":"Jesper Myrfors","power":"9","toughness":"9","manaCost":"{9}","text":"Trample (If this creature would assign enough damage to its blockers to destroy them, you may have it assign the rest of its damage to defending player or planeswalker.)\\nColossus of Sardia doesn't untap during your untap step.\\n{9}: Untap Colossus of Sardia. Activate this ability only during your upkeep.","originalText":"Trample\\nColossus does not untap normally during untap phase; you may spend {9} during your upkeep phase to untap Colossus.","flavor":"From the Sardian mountains wakes ancient doom:\\nWarrior born from a rocky womb.","rulings":[{"date":"2008-05-01","text":"The ability that untaps it during your upkeep has been returned to an activated ability. There is no restriction on how many times it can be untapped during your upkeep with this ability."}],"imageName":"colossus of sardia","foreignNames":[{"language":"Chinese Simplified","name":"沙地亚巨像"},{"language":"Chinese Traditional","name":"沙地亞巨像"},{"language":"French","name":"Colosse de Sardie"},{"language":"German","name":"Der Koloss von Sardia"},{"language":"Italian","name":"Colosso di Sardia"},{"language":"Japanese","name":"サルディアの巨像"},{"language":"Portuguese (Brazil)","name":"Colosso de Sardia"},{"language":"Russian","name":"Колосс Сардии"},{"language":"Spanish","name":"Coloso de Sardia"}],"legalities":{"Modern":"Legal","Legacy":"Legal","Vintage":"Legal","Freeform":"Legal","Prismatic":"Legal","Tribal Wars Legacy":"Legal","Singleton 100":"Legal","Commander":"Legal"},"printings":["Antiquities","Fourth Edition","Fifth Edition","Tenth Edition","Masters Edition IV"]}'''

    black_lotus_json = '''{"layout":"normal",
"type":"Artifact",
"types":["Artifact"],
"multiverseid":3,
"name":"Black Lotus",
"originalType":"Mono Artifact",
"cmc":0,
"rarity":"Rare",
"artist":"Christopher Rush",
"manaCost":"{0}",
"text":"{T}, Sacrifice Black Lotus: Add three mana of any one color to your mana pool.",
"originalText":"Adds 3 mana of any single color of your choice to your mana pool, then is discarded. Tapping this artifact can be played as an interrupt.",
"imageName":"black lotus",
"legalities":{"Legacy":"Banned","Vintage":"Restricted","Freeform":"Legal","Prismatic":"Legal","Commander":"Banned"},
"printings":["Limited Edition Alpha","Limited Edition Beta","Unlimited Edition","Vintage Masters"],
"reserved":true}
'''
    cavern_of_souls_json = '''{"layout":"normal",
"type":"Land",
"types":["Land"],
"multiverseid":278058,
"name":"Cavern of Souls",
"originalType":"Land",
"rarity":"Rare",
"artist":"Cliff Childs",
"text":"As Cavern of Souls enters the battlefield, choose a creature type.\\n{T}: Add {1} to your mana pool.\\n{T}: Add one mana of any color to your mana pool. Spend this mana only to cast a creature spell of the chosen type, and that spell can't be countered.",
"originalText":"As Cavern of Souls enters the battlefield, choose a creature type.\\n{T}: Add {1} to your mana pool.\\n{T}: Add one mana of any color to your mana pool. Spend this mana only to cast a creature spell of the chosen type, and that spell can't be countered.",
"number":"226",
"rulings":[
 {"date":"2012-05-01",
  "text":"You must choose an existing _Magic_ creature type, such as Zombie or Warrior. Card types such as artifact can't be chosen."},
 {"date":"2012-05-01",
  "text":"The spell can't be countered if the mana produced by Cavern of Souls is spent to cover any cost of the spell, even an additional cost such as a kicker cost. This is true even if you use the mana to pay an additional cost while casting a spell \\"without paying its mana cost.\\""}],
"imageName":"cavern of souls",
"foreignNames":[{"language":"Chinese Traditional","name":"靈魂洞窟"},{"language":"Chinese Simplified","name":"灵魂洞窟"},{"language":"French","name":"Caverne des âmes"},{"language":"German","name":"Seelengewölbe"},{"language":"Italian","name":"Grotta delle Anime"},{"language":"Japanese","name":"魂の洞窟"},{"language":"Korean","name":"영혼의 동굴"},{"language":"Portuguese (Brazil)","name":"Caverna das Almas"},{"language":"Russian","name":"Пещера Душ"},{"language":"Spanish","name":"Caverna de ánimas"}],
"legalities":{"Modern":"Legal","Innistrad Block":"Legal","Legacy":"Legal","Vintage":"Legal","Freeform":"Legal","Prismatic":"Legal","Tribal Wars Legacy":"Legal","Tribal Wars Standard":"Legal","Singleton 100":"Legal","Commander":"Legal"},
"printings":["Avacyn Restored"]}'''

    garruks_companion_json = '''{"layout":"normal","type":"Creature — Beast","types":["Creature"],"colors":["Green"],"multiverseid":205025,"name":"Garruk's Companion","subtypes":["Beast"],"originalType":"Creature — Beast","cmc":2,"rarity":"Common","artist":"Efrem Palacios","power":"3","toughness":"2","manaCost":"{G}{G}","text":"Trample (If this creature would assign enough damage to its blockers to destroy them, you may have it assign the rest of its damage to defending player or planeswalker.)","originalText":"Trample (If this creature would assign enough damage to its blockers to destroy them, you may have it assign the rest of its damage to defending player or planeswalker.)","number":"176","imageName":"garruk's companion","foreignNames":[{"language":"Chinese Traditional","name":"賈路的旅伴"},{"language":"Chinese Simplified","name":"贾路的旅伴"},{"language":"French","name":"Compagnon de Garruk"},{"language":"German","name":"Garruks Begleiter"},{"language":"Italian","name":"Compagno di Garruk"},{"language":"Japanese","name":"ガラクの仲間"},{"language":"Portuguese (Brazil)","name":"Companheiro de Garruk"},{"language":"Russian","name":"Спутник Гаррука"},{"language":"Spanish","name":"Compañero de Garruk"}],"legalities":{"Modern":"Legal","Legacy":"Legal","Vintage":"Legal","Freeform":"Legal","Prismatic":"Legal","Tribal Wars Legacy":"Legal","Singleton 100":"Legal","Commander":"Legal"},"printings":["Magic 2011","Magic 2012"]}
'''

    break_through_json = '''{"layout":"normal","type":"Enchantment","types":["Enchantment"],"colors":["Red"],"multiverseid":391805,"name":"Break Through the Line","originalType":"Enchantment","cmc":2,"rarity":"Uncommon","artist":"Clint Cearley","manaCost":"{1}{R}","text":"{R}: Target creature with power 2 or less gains haste until end of turn and can't be blocked this turn.","originalText":"{R}: Target creature with power 2 or less gains haste until end of turn and can't be blocked this turn.","flavor":"\\"If the Mardu were more in tune with their beasts, they would not scare so easily.\\"\\n—Jilaya, Temur whisperer","number":"94","imageName":"break through the line","foreignNames":[{"language":"Chinese Traditional","name":"突破防線"},{"language":"Chinese Simplified","name":"突破防线"},{"language":"French","name":"Briser les rangs"},{"language":"German","name":"Die Linien durchbrechen"},{"language":"Italian","name":"Sfondare la Linea"},{"language":"Japanese","name":"戦線突破"},{"language":"Korean","name":"전선 돌파"},{"language":"Portuguese (Brazil)","name":"Romper as Fileiras"},{"language":"Russian","name":"Прорвать Ряды"},{"language":"Spanish","name":"Atravesar las filas"}],"printings":["Fate Reforged"],"legalities":{"Vintage":"Legal"}}'''

    arcbond_json = '''{"layout":"normal","type":"Instant","types":["Instant"],"colors":["Red"],"multiverseid":391793,"name":"Arcbond","originalType":"Instant","cmc":3,"rarity":"Rare","artist":"Slawomir Maniak","manaCost":"{2}{R}","text":"Choose target creature. Whenever that creature is dealt damage this turn, it deals that much damage to each other creature and each player.","originalText":"Choose target creature. Whenever that creature is dealt damage this turn, it deals that much damage to each other creature and each player.","flavor":"\\"If you must die today, make your death worthy of legend.\\"\\n—Alesha, Who Smiles at Death","number":"91","imageName":"arcbond","foreignNames":[{"language":"Chinese Traditional","name":"電弧連心"},{"language":"Chinese Simplified","name":"电弧连心"},{"language":"French","name":"Arc enchaîneur"},{"language":"German","name":"Überspringender Lichtbogen"},{"language":"Italian","name":"Vincolo Elettrico"},{"language":"Japanese","name":"電弧連鎖"},{"language":"Korean","name":"번개묶기"},{"language":"Portuguese (Brazil)","name":"Propagação Elétrica"},{"language":"Russian","name":"Громовая Дуга"},{"language":"Spanish","name":"Electrizarco"}],"printings":["Fate Reforged"],"legalities":{"Vintage":"Legal"}}'''

    cached_defenses_json = '''{"layout":"normal","type":"Sorcery","types":["Sorcery"],"colors":["Green"],"multiverseid":391807,"name":"Cached Defenses","originalType":"Sorcery","cmc":3,"rarity":"Uncommon","artist":"Zack Stella","manaCost":"{2}{G}","text":"Bolster 3. (Choose a creature with the least toughness among creatures you control and put three +1/+1 counters on it.)","originalText":"Bolster 3. (Choose a creature with the least toughness among creatures you control and put three +1/+1 counters on it.)","flavor":"The glittering scales in the Abzan vaults represent mighty deeds of the past and protection for generations to come.","number":"126","watermark":"Temur","imageName":"cached defenses","foreignNames":[{"language":"Chinese Traditional","name":"密儲防衛"},{"language":"Chinese Simplified","name":"密储防卫"},{"language":"French","name":"Défenses en réserve"},{"language":"German","name":"Gelagerte Verteidigung"},{"language":"Italian","name":"Difese Occulte"},{"language":"Japanese","name":"隠匿物の防衛"},{"language":"Korean","name":"숨겨진 방어구"},{"language":"Portuguese (Brazil)","name":"Defesas Acumuladas"},{"language":"Russian","name":"Оборонительные Запасы"},{"language":"Spanish","name":"Defensas ocultas"}],"printings":["Fate Reforged"],"legalities":{"Vintage":"Legal"}}'''
    
    island_json = '''{"layout":"normal","supertypes":["Basic"],"type":"Basic Land — Island","types":["Land"],"multiverseid":391859,"name":"Island","subtypes":["Island"],"originalType":"Basic Land — Island","rarity":"Basic Land","artist":"Florian de Gesincourt","originalText":"U","number":"178","variations":[391860],"imageName":"island1","foreignNames":[{"language":"Chinese Simplified","name":"海岛"},{"language":"Chinese Traditional","name":"海島"},{"language":"French","name":"Île"},{"language":"German","name":"Insel"},{"language":"Italian","name":"Isola"},{"language":"Japanese","name":"島"},{"language":"Korean","name":"섬"},{"language":"Portuguese (Brazil)","name":"Ilha"},{"language":"Russian","name":"Остров"},{"language":"Spanish","name":"Isla"}],"legalities":{"Standard":"Legal","Modern":"Legal","Theros Block":"Legal","Return to Ravnica Block":"Legal","Innistrad Block":"Legal","Scars of Mirrodin Block":"Legal","Zendikar Block":"Legal","Shards of Alara Block":"Legal","Lorwyn-Shadowmoor Block":"Legal","Time Spiral Block":"Legal","Ravnica Block":"Legal","Kamigawa Block":"Legal","Mirrodin Block":"Legal","Onslaught Block":"Legal","Odyssey Block":"Legal","Invasion Block":"Legal","Masques Block":"Legal","Urza Block":"Legal","Tempest Block":"Legal","Mirage Block":"Legal","Ice Age Block":"Legal","Un-Sets":"Legal","Legacy":"Legal","Vintage":"Legal","Freeform":"Legal","Prismatic":"Legal","Tribal Wars Legacy":"Legal","Tribal Wars Standard":"Legal","Singleton 100":"Legal","Commander":"Legal"},"printings":["Limited Edition Alpha","Limited Edition Beta","Unlimited Edition","Revised Edition","Fourth Edition","Ice Age","Rivals Quick Start Set","Arena League","Mirage","Introductory Two-Player Set","Fifth Edition","Portal","Tempest","Judge Gift Program","Portal Second Age","Unglued","Asia Pacific Land Program","Urza's Saga","Classic Sixth Edition","Portal Three Kingdoms","Starter 1999","Guru","Mercadian Masques","Battle Royale Box Set","European Land Program","Starter 2000","Beatdown Box Set","Invasion","Seventh Edition","Odyssey","Onslaught","Eighth Edition","Mirrodin","Champions of Kamigawa","Unhinged","Ninth Edition","Ravnica: City of Guilds","Coldsnap Theme Decks","Time Spiral","Tenth Edition","Masters Edition","Lorwyn","Shadowmoor","Shards of Alara","Duel Decks: Jace vs. Chandra","Magic 2010","Planechase","Masters Edition III","Zendikar","Premium Deck Series: Slivers","Duel Decks: Phyrexia vs. the Coalition","Rise of the Eldrazi","Duels of the Planeswalkers","Archenemy","Magic 2011","Duel Decks: Elspeth vs. Tezzeret","Scars of Mirrodin","Mirrodin Besieged","New Phyrexia","Magic: The Gathering-Commander","Magic 2012","Duel Decks: Ajani vs. Nicol Bolas","Innistrad","Duel Decks: Venser vs. Koth","Avacyn Restored","Planechase 2012 Edition","Magic 2013","Duel Decks: Izzet vs. Golgari","Return to Ravnica","Magic 2014 Core Set","Theros","Commander 2013 Edition","Duel Decks: Jace vs. Vraska","Magic 2015 Core Set","Duel Decks: Speed vs. Cunning","Khans of Tarkir","Commander 2014","Fate Reforged"]}'''

    crucible_land_json = '''{"layout":"normal","type":"Land","types":["Land"],"multiverseid":391812,"name":"Crucible of the Spirit Dragon","originalType":"Land","rarity":"Rare","artist":"Jung Park","text":"{T}: Add {1} to your mana pool.\\n{1}, {T}: Put a storage counter on Crucible of the Spirit Dragon.\\n{T}, Remove X storage counters from Crucible of the Spirit Dragon: Add X mana in any combination of colors to your mana pool. Spend this mana only to cast Dragon spells or activate abilities of Dragons.","originalText":"{T}: Add {1} to your mana pool.\\n{1}, {T}: Put a storage counter on Crucible of the Spirit Dragon.\\n{T}, Remove X storage counters from Crucible of the Spirit Dragon: Add X mana in any combination of colors to your mana pool. Spend this mana only to cast Dragon spells or activate abilities of Dragons.","number":"167","imageName":"crucible of the spirit dragon","foreignNames":[{"language":"Chinese Traditional","name":"靈龍蟄居"},{"language":"Chinese Simplified","name":"灵龙蛰居"},{"language":"French","name":"Creuset du dragon-esprit"},{"language":"German","name":"Hort des Geisterdrachen"},{"language":"Italian","name":"Crogiolo dello Spirito Drago"},{"language":"Japanese","name":"精霊龍のるつぼ"},{"language":"Korean","name":"신령 용의 유폐지"},{"language":"Portuguese (Brazil)","name":"Crisol do Dragão Espírito"}{"language":"Russian","name":"Горнило Духа Дракона"},{"language":"Spanish","name":"Crisol del dragón espíritu"}],"printings":["Fate Reforged"],"legalities":{"Vintage":"Legal"}}'''

    hyena_umbra_json = '''{"layout":"normal","type":"Enchantment — Aura","types":["Enchantment"],"colors":["White"],"multiverseid":198294,"name":"Hyena Umbra","subtypes":["Aura"],"originalType":"Enchantment — Aura","cmc":1,"rarity":"Common","artist":"Howard Lyon","manaCost":"{W}","text":"Enchant creature\nEnchanted creature gets +1/+1 and has first strike.\nTotem armor (If enchanted creature would be destroyed, instead remove all damage from it and destroy this Aura.)","originalText":"Enchant creature\nEnchanted creature gets +1/+1 and has first strike.\nTotem armor (If enchanted creature would be destroyed, instead remove all damage from it and destroy this Aura.)","number":"26","rulings":[{"date":"2010-06-15","text":"Totem armor's effect is mandatory. If the enchanted permanent would be destroyed, you must remove all damage from it and destroy the Aura that has totem armor instead."},{"date":"2010-06-15","text":"Totem armor's effect is applied no matter why the enchanted permanent would be destroyed: because it's been dealt lethal damage, or because it's being affected by an effect that says to \"destroy\" it (such as Doom Blade). In either case, all damage is removed from the permanent and the Aura is destroyed instead."},{"date":"2010-06-15","text":"If a permanent you control is enchanted with multiple Auras that have totem armor, and the enchanted permanent would be destroyed, one of those Auras is destroyed instead -- but only one of them. You choose which one because you control the enchanted permanent."},{"date":"2010-06-15","text":"If a creature enchanted with an Aura that has totem armor would be destroyed by multiple state-based actions at the same time the totem armor's effect will replace all of them and save the creature."},{"date":"2010-06-15","text":"If a spell or ability (such as Planar Cleansing) would destroy both an Aura with totem armor and the permanent it's enchanting at the same time, totem armor's effect will save the enchanted permanent from being destroyed. Instead, the spell or ability will destroy the Aura in two different ways at the same time, but the result is the same as destroying it once."},{"date":"2010-06-15","text":"Totem armor's effect is not regeneration. Specifically, if totem armor's effect is applied, the enchanted permanent does not become tapped and is not removed from combat as a result. Effects that say the enchanted permanent can't be regenerated (as Vendetta does) won't prevent totem armor's effect from being applied."},{"date":"2010-06-15","text":"Say you control a permanent enchanted with an Aura that has totem armor, and the enchanted permanent has gained a regeneration shield. The next time it would be destroyed, you choose whether to apply the regeneration effect or the totem armor effect. The other effect is unused and remains, in case the permanent would be destroyed again."},{"date":"2010-06-15","text":"If a spell or ability says that it would \"destroy\" a permanent enchanted with an Aura that has totem armor, that spell or ability causes the Aura to be destroyed instead. (This matters for cards such as Karmic Justice.) Totem armor doesn't destroy the Aura; rather, it changes the effects of the spell or ability. On the other hand, if a spell or ability deals lethal damage to a creature enchanted with an Aura that has totem armor, the game rules regarding lethal damage cause the Aura to be destroyed, not that spell or ability."},{"date":"2013-07-01","text":"Totem armor has no effect if the enchanted permanent is put into a graveyard for any other reason, such as if it's sacrificed, if it's legendary and another legendary permanent with the same name is controlled by the same player, or if its toughness is 0 or less."},{"date":"2013-07-01","text":"If a creature enchanted with an Aura that has totem armor has indestructible, lethal damage and effects that try to destroy it simply have no effect. Totem armor won't do anything because it won't have to."},{"date":"2013-07-01","text":"Say you control a permanent enchanted with an Aura that has totem armor, and that Aura has gained a regeneration shield. The next time the enchanted permanent would be destroyed, the Aura would be destroyed instead -- but it regenerates, so nothing is destroyed at all. Alternately, if that Aura somehow gains indestructible, the enchanted permanent is effectively indestructible as well."}],"imageName":"hyena umbra","foreignNames":[{"language":"Chinese Simplified","name":"鬣狗本影"},{"language":"French","name":"Ombre de hyène"},{"language":"German","name":"Schattenhafte Hyäne"},{"language":"Italian","name":"Essenza della Iena"},{"language":"Japanese","name":"ハイエナの陰影"},{"language":"Portuguese (Brazil)","name":"Sombra de Hiena"},{"language":"Russian","name":"Дух Гиены"},{"language":"Spanish","name":"Umbra de hiena"}],"legalities":{"Modern":"Legal","Zendikar Block":"Legal","Legacy":"Legal","Vintage":"Legal","Freeform":"Legal","Prismatic":"Legal","Tribal Wars Legacy":"Legal","Singleton 100":"Legal","Commander":"Legal"},"printings":["Rise of the Eldrazi","Planechase 2012 Edition"]}'''

    azorius_guildgate_json = '''{"layout":"normal","type":"Land — Gate","types":["Land"],"multiverseid":270966,"name":"Azorius Guildgate","subtypes":["Gate"],"originalType":"Land — Gate","rarity":"Common","artist":"Drew Baker","text":"Azorius Guildgate enters the battlefield tapped.\\n{T}: Add {W} or {U} to your mana pool.","originalText":"Azorius Guildgate enters the battlefield tapped.\\n{T}: Add {W} or {U} to your mana pool.","flavor":"Enter the Senate, the seat of justice and the foundation of Ravnican society.","number":"237","watermark":"Azorius","rulings":[{"date":"2013-04-15","text":"The subtype Gate has no special rules significance, but other spells and abilities may refer to it."},{"date":"2013-04-15","text":"Gate is not a basic land type."}],"imageName":"azorius guildgate","foreignNames":[{"language":"Chinese Traditional","name":"俄佐立公會門"},{"language":"Chinese Simplified","name":"俄佐立公会门"},{"language":"French","name":"Porte de la guilde d'Azorius"},{"language":"German","name":"Azorius-Gildeneingang"},{"language":"Italian","name":"Cancello della Gilda Azorius"},{"language":"Japanese","name":"アゾリウスのギルド門"},{"language":"Korean","name":"아조리우스 길드관문"},{"language":"Portuguese (Brazil)","name":"Portão da Guilda Azorius"},{"language":"Russian","name":"Врата Гильдии Азориусов"},{"language":"Spanish","name":"Portal del Gremio Azorio"}],"legalities":{"Modern":"Legal","Return to Ravnica Block":"Legal","Legacy":"Legal","Vintage":"Legal","Freeform":"Legal","Prismatic":"Legal","Tribal Wars Legacy":"Legal","Tribal Wars Standard":"Legal","Singleton 100":"Legal","Commander":"Legal"},"printings":["Return to Ravnica","Dragon's Maze","Commander 2013 Edition"]}'''

    azorius_justicar_json = '''{"layout":"normal","type":"Creature — Human Wizard","types":["Creature"],"colors":["White"],"multiverseid":270795,"name":"Azorius Justiciar","subtypes":["Human","Wizard"],"originalType":"Creature — Human Wizard","cmc":4,"rarity":"Uncommon","artist":"Chris Rahn","power":"2","toughness":"2","manaCost":"{2}{W}{W}","text":"When Azorius Justiciar enters the battlefield, detain up to two target creatures your opponents control. (Until your next turn, those creatures can't attack or block and their activated abilities can't be activated.)","originalText":"When Azorius Justiciar enters the battlefield, detain up to two target creatures your opponents control. (Until your next turn, those creatures can't attack or block and their activated abilities can't be activated.)","flavor":"\\"Your potential to commit a crime warrants further investigation.\\"","number":"6","watermark":"Azorius","rulings":[{"date":"2012-10-01","text":"The two creatures can be controlled by the same opponent or by different opponents."},{"date":"2013-04-15","text":"Activated abilities include a colon and are written in the form “[cost]: [effect].” No one can activate any activated abilities, including mana abilities, of a detained permanent."},{"date":"2013-04-15","text":"The static abilities of a detained permanent still apply. The triggered abilities of a detained permanent can still trigger."},{"date":"2013-04-15","text":"If a creature is already attacking or blocking when it's detained, it won't be removed from combat. It will continue to attack or block."},{"date":"2013-04-15","text":"If a permanent's activated ability is on the stack when that permanent is detained, the ability will be unaffected."},{"date":"2013-04-15","text":"If a noncreature permanent is detained and later turns into a creature, it won't be able to attack or block."},{"date":"2013-04-15","text":"When a player leaves a multiplayer game, any continuous effects with durations that last until that player's next turn or until a specific point in that turn will last until that turn would have begun. They neither expire immediately nor last indefinitely."}],"imageName":"azorius justiciar","foreignNames":[{"language":"Chinese Traditional","name":"俄佐立大司法"},{"language":"Chinese Simplified","name":"俄佐立大司法"},{"language":"French","name":"Justicière d'Azorius"},{"language":"German","name":"Azorius-Justiziarin"},{"language":"Italian","name":"Magistrato Azorius"},{"language":"Japanese","name":"アゾリウスの大司法官"},{"language":"Korean","name":"아조리우스 재판관"},{"language":"Portuguese (Brazil)","name":"Justiciar Azorius"},{"language":"Russian","name":"Юстициар Азориусов"},{"language":"Spanish","name":"Justiciar azorio"}],"legalities":{"Modern":"Legal","Return to Ravnica Block":"Legal","Legacy":"Legal","Vintage":"Legal","Freeform":"Legal","Prismatic":"Legal","Tribal Wars Legacy":"Legal","Tribal Wars Standard":"Legal","Singleton 100":"Legal","Commander":"Legal"},"printings":["Return to Ravnica"]}'''

    ikiral_outrider_json = '''{"layout":"leveler","type":"Creature — Human Soldier","types":["Creature"],"colors":["White"],"multiverseid":198176,"name":"Ikiral Outrider","subtypes":["Human","Soldier"],"originalType":"Creature — Human Soldier","cmc":2,"rarity":"Common","artist":"Kekai Kotaki","power":"1","toughness":"2","manaCost":"{1}{W}","text":"Level up {4} ({4}: Put a level counter on this. Level up only as a sorcery.)\\nLEVEL 1-3\\n2/6\\nVigilance\\nLEVEL 4+\\n3/10\\nVigilance","originalText":"Level up {4} ({4}: Put a level counter on this. Level up only as a sorcery.)\\nLEVEL 1-3\\n2/6\\nVigilance\\nLEVEL 4+\\n3/10\\nVigilance","number":"27","rulings":[{"date":"2010-06-15","text":"The abilities a leveler grants to itself don't overwrite any other abilities it may have. In particular, they don't overwrite the creature's level up ability; it always has that."},{"date":"2010-06-15","text":"Effects that set a leveler's power or toughness to a specific value, including the effects from a level symbol's ability, apply in timestamp order. The timestamp of each level symbol's ability is the same as the timestamp of the leveler itself, regardless of when the most recent level counter was put on it."},{"date":"2010-06-15","text":"Effects that modify a leveler's power or toughness, such as the effects of Giant Growth or Glorious Anthem, will apply to it no matter when they started to take effect. The same is true for counters that change the creature's power or toughness (such as +1/+1 counters) and effects that switch its power and toughness."},{"date":"2010-06-15","text":"If another creature becomes a copy of a leveler, all of the leveler's printed abilities -- including those represented by level symbols -- are copied. The current characteristics of the leveler, and the number of level counters on it, are not. The abilities, power, and toughness of the copy will be determined based on how many level counters are on the copy."},{"date":"2010-06-15","text":"A creature's level is based on how many level counters it has on it, not how many times its level up ability has been activated or has resolved. If a leveler gets level counters due to some other effect (such as Clockspinning) or loses level counters for some reason (such as Vampire Hexmage), its level is changed accordingly."}],"imageName":"ikiral outrider","foreignNames":[{"language":"Chinese Simplified","name":"伊奇洛前导兵"},{"language":"French","name":"Cavalier d'Ikiral"},{"language":"German","name":"Vorreiter aus Ikiral"},{"language":"Italian","name":"Apripista di Ikiral"},{"language":"Japanese","name":"イキーラルの先導"},{"language":"Portuguese (Brazil)","name":"Vanguardeiro de Ikiral"},{"language":"Russian","name":"Икиральский Верховой"},{"language":"Spanish","name":"Batidor de Ikiral"}],"legalities":{"Modern":"Legal","Zendikar Block":"Legal","Legacy":"Legal","Vintage":"Legal","Freeform":"Legal","Prismatic":"Legal","Tribal Wars Legacy":"Legal","Singleton 100":"Legal","Commander":"Legal"},"printings":["Rise of the Eldrazi"]}'''

    induce_despair_json = '''{"layout":"normal","type":"Instant","types":["Instant"],"colors":["Black"],"multiverseid":193520,"name":"Induce Despair","originalType":"Instant","cmc":3,"rarity":"Common","artist":"Igor Kieryluk","manaCost":"{2}{B}","text":"As an additional cost to cast Induce Despair, reveal a creature card from your hand.\\nTarget creature gets -X/-X until end of turn, where X is the revealed card's converted mana cost.","originalText":"As an additional cost to cast Induce Despair, reveal a creature card from your hand.\\nTarget creature gets -X/-X until end of turn, where X is the revealed card's converted mana cost.","flavor":"All the angel saw was her doom.","number":"114","imageName":"induce despair","foreignNames":[{"language":"Chinese Simplified","name":"引致绝望"},{"language":"French","name":"Invitation au désespoir"},{"language":"German","name":"Verzweifeln lassen"},{"language":"Italian","name":"Spingere alla Disperazione"},{"language":"Japanese","name":"絶望の誘導"},{"language":"Portuguese (Brazil)","name":"Induzir Desespero"},{"language":"Russian","name":"Приступ Отчаяния"},{"language":"Spanish","name":"Inducir a la desesperación"}],"legalities":{"Modern":"Legal","Zendikar Block":"Legal","Legacy":"Legal","Vintage":"Legal","Freeform":"Legal","Prismatic":"Legal","Tribal Wars Legacy":"Legal","Singleton 100":"Legal","Commander":"Legal"},"printings":["Rise of the Eldrazi"]}'''

    alesha_json = '''{"layout":"normal","supertypes":["Legendary"],"type":"Legendary Creature — Human Warrior","types":["Creature"],"colors":["Red"],"multiverseid":391787,"name":"Alesha, Who Smiles at Death","subtypes":["Human","Warrior"],"originalType":"Legendary Creature — Human Warrior","cmc":3,"rarity":"Rare","artist":"Anastasia Ovchinnikova","power":"3","toughness":"2","manaCost":"{2}{R}","text":"First strike\\nWhenever Alesha, Who Smiles at Death attacks, you may pay {W/B}{W/B}. If you do, return target creature card with power 2 or less from your graveyard to the battlefield tapped and attacking.","originalText":"First strike\\nWhenever Alesha, Who Smiles at Death attacks, you may pay {W/B}{W/B}. If you do, return target creature card with power 2 or less from your graveyard to the battlefield tapped and attacking.","flavor":"\\"Greet death with sword in hand.\\"","number":"90","watermark":"Mardu","imageName":"alesha, who smiles at death","foreignNames":[{"language":"Chinese Traditional","name":"蔑死者阿列莎"},{"language":"Chinese Simplified","name":"蔑死者阿列莎"},{"language":"French","name":"Alesha, Celle-qui-sourit-devant-la-mort"},{"language":"German","name":"Alesha, Verachterin des Todes"},{"language":"Italian","name":"Alesha, Che Sorride alla Morte"},{"language":"Japanese","name":"死に微笑むもの、アリーシャ"},{"language":"Korean","name":"죽음에 웃음짓는 알레샤"},{"language":"Portuguese (Brazil)","name":"Alesha, a Que Sorri Para a Morte"},{"language":"Russian","name":"Алиша, Улыбнувшаяся Смерти"},{"language":"Spanish","name":"Alesha, la que sonríe a la muerte"}],"printings":["Fate Reforged"],"legalities":{"Vintage":"Legal"}}'''

    def load_card(self, json, name, loadhelper=True, set_abbr='BAR'):
        helper = TestLoadHelper()
        if loadhelper:
            helper.expansionset_example_loader()
        expset = ExpansionSet.objects.filter(abbr=set_abbr).first()
        tool = Command()
        tool.handle_card_json(json, expset)
        card = BaseCard.objects.filter(name=name).first()
        return card
    
    def test_type_single_artifact(self):
        card = self.load_card(self.black_lotus_json, 'Black Lotus')
        self.assertEquals(card.types.count(), 1)
        self.assertEquals(card.types.all().first().type, 'Artifact')

    def test_type_single_land(self):
        card = self.load_card(self.cavern_of_souls_json, 'Cavern of Souls')
        self.assertEquals(card.types.count(), 1)
        self.assertEquals(card.types.all().first().type, 'Land')

    def test_type_single_creature(self):
        card = self.load_card(self.garruks_companion_json, "Garruk's Companion")
        self.assertEquals(card.types.count(), 1)
        self.assertEquals(card.types.all().first().type, 'Creature')

    def test_type_single_enchantment(self):
        card = self.load_card(self.break_through_json, 'Break Through the Line')
        self.assertEquals(card.types.count(), 1)
        self.assertEquals(card.types.all().first().type, 'Enchantment')

    def test_type_single_instant(self):
        card = self.load_card(self.arcbond_json, 'Arcbond')
        self.assertEquals(card.types.count(), 1)
        self.assertEquals(card.types.all().first().type, 'Instant')


    def test_type_single_sorcery(self):
        card = self.load_card(self.cached_defenses_json, 'Cached Defenses')
        self.assertEquals(card.types.count(), 1)
        self.assertEquals(card.types.all().first().type, 'Sorcery')

    def test_subtype_none_1(self):
        card = self.load_card(self.arcbond_json, 'Arcbond')
        self.assertEquals(card.subtypes.count(), 0)

    def test_subtype_none_2(self):
        card = self.load_card(self.cavern_of_souls_json, 'Cavern of Souls')
        self.assertEquals(card.subtypes.count(), 0)

    def test_subtype_single_creature(self):
        card = self.load_card(self.garruks_companion_json, "Garruk's Companion")
        self.assertEquals(card.subtypes.count(), 1)
        self.assertEquals(card.subtypes.all().first().subtype, 'Beast')

    def test_name_oneword(self):
        card = self.load_card(self.arcbond_json, "Arcbond")
        self.assertEquals(card.name, 'Arcbond')
        self.assertEquals(card.filing_name, 'arcbond')

    def test_name_threewords(self):
        card = self.load_card(self.cavern_of_souls_json, 'Cavern of Souls')
        self.assertEquals(card.name, 'Cavern of Souls')
        self.assertEquals(card.filing_name, 'cavern of souls')

    def test_name_apostrophe(self):
        card = self.load_card(self.garruks_companion_json, "Garruk's Companion")
        self.assertEquals(card.name, 'Garruk\'s Companion')
        self.assertEquals(card.filing_name, 'garruks companion')

    # def test_name_10000(self):
    #     self.assertTrue(False)

    # def test_name_unicode(self):
    #     self.assertTrue(False)

    # def test_name_unicode_ae(self):
    #     self.assertTrue(False)

#    def test_name_dash(self):
#        self.assertTrue(False)

#    def test_name_comma(self):
#        self.assertTrue(False)

    def test_cmc_0_simple(self):
        card = self.load_card(self.black_lotus_json, 'Black Lotus')
        self.assertEquals(card.cmc, 0)
        self.assertEquals(card.mana_cost, '{0}')

    def test_cmc_land_simple(self):
        card = self.load_card(self.cavern_of_souls_json, 'Cavern of Souls')
        self.assertEquals(card.cmc, 0)
        self.assertEquals(card.mana_cost, '')

    def test_cmc_2_1r(self):
        card = self.load_card(self.break_through_json, 'Break Through the Line')
        self.assertEquals(card.cmc, 2)
        self.assertEquals(card.mana_cost, '{1}{r}')

    def test_cmc_2_gg(self):
        card = self.load_card(self.garruks_companion_json, "Garruk's Companion")
        self.assertEquals(card.cmc, 2)
        self.assertEquals(card.mana_cost, '{g}{g}')


#    def test_to_make_sure_types_are_being_reused(self):
#        self.assertTrue(False)
        
    def test_types_legendary(self):
        card = self.load_card(self.alesha_json, "Alesha, Who Smiles at Death")
        self.assertGreater(card.types.count(), 1)
        self.assertEquals(card.types.all().first().type, 'Legendary')

#    def test_types_three(self):
#        self.assertTrue(False)

#    def test_subtypes_single_aura(self):
#        self.assertTrue(False)

    def test_subtypes_single_land(self):
        card = self.load_card(self.azorius_guildgate_json, "Azorius Guildgate")
        self.assertEquals(card.cmc, 0)
        self.assertEquals(card.mana_cost, '')
        self.assertEquals(card.subtypes.count(), 1)
        self.assertEquals(card.subtypes.all().first().subtype, 'Gate')

#    def test_subtypes_single_land_urzas(self):
#        self.assertTrue(False)

    def test_subtypes_new(self):
        card = self.load_card(self.magnivore_json, "Magnivore")
        self.assertEquals(card.subtypes.count(), 1)
        self.assertEquals(card.subtypes.all().first().subtype, 'Lhurgoyf')

    def test_types_two(self):
        card = self.load_card(self.alesha_json, "Alesha, Who Smiles at Death")
        self.assertEquals(card.types.count(), 2)
        self.assertEquals(card.types.all().first().type, 'Legendary')
        self.assertEquals(card.types.all()[1].type, 'Creature')

    def test_subtypes_two(self):
        card = self.load_card(self.alesha_json, "Alesha, Who Smiles at Death")
        self.assertEquals(card.subtypes.count(), 2)
        self.assertEquals(card.subtypes.all().first().subtype, 'Human')
        self.assertEquals(card.subtypes.all()[1].subtype, 'Warrior')

#    def test_subtypes_two_new(self):
#        self.assertTrue(False)

#    def test_subtypes_three(self):
#        self.assertTrue(False)

    def test_cmc_2(self):
        card = self.load_card(self.garruks_companion_json, "Garruk's Companion")
        self.assertEquals(card.cmc, 2)
        self.assertEquals(card.mana_cost, '{g}{g}')

    def test_cmc_3(self):
        card = self.load_card(self.induce_despair_json, "Induce Despair")
        self.assertEquals(card.cmc, 3)
        self.assertEquals(card.mana_cost, '{2}{b}')

    def test_cmc_9(self):
        card = self.load_card(self.colossus_sardia_json, "Colossus of Sardia")
        self.assertEquals(card.cmc, 9)
        self.assertEquals(card.mana_cost, '{9}')

    def test_manacost_0(self):
        card = self.load_card(self.black_lotus_json, 'Black Lotus')
        self.assertEquals(card.cmc, 0)
        self.assertEquals(card.mana_cost, '{0}')

    # def test_manacost_1up(self):
    #     self.assertTrue(False)
    # def test_manacost_1bpbp(self):
    #     self.assertTrue(False)
    # def test_manacost_uw(self):
    #     self.assertTrue(False)
    # def test_manacost_2w(self):
    #     self.assertTrue(False)
    # def test_manacost_none_spell(self):
    #     self.assertTrue(False)
    # def test_manacost_rwrwrw(self):
    #     self.assertTrue(False)

    # def test_split_card(self):
    #     self.assertTrue(False)

    # def test_flip_card(self):
    #     self.assertTrue(False)

    # def test_planeswalker_card(self):
    #     self.assertTrue(False)

    def test_type_double_card(self):
        card = self.load_card(self.huntmaster_json, "Huntmaster of the Fells")
        card2 = self.load_card(self.ravager_json, "Ravager of the Fells", loadhelper=False)
        pcard = card.physicalcard
        self.assertEquals(pcard.layout, pcard.DOUBLE)
        pcard2 = card.physicalcard
        self.assertEquals(pcard2.layout, pcard.DOUBLE)
        self.assertEquals(pcard, pcard2)

        self.assertEquals(card.name, 'Huntmaster of the Fells')
        self.assertEquals(card.cardposition, card.FRONT)
        self.assertEquals(card2.name, 'Ravager of the Fells')
        self.assertEquals(card2.cardposition, card.BACK)

        hunt = card.card_set.all().first()
        ravager = card2.card_set.all().first()

        self.assertEquals(hunt, ravager.get_double_faced_card())
        self.assertEquals(ravager, hunt.get_double_faced_card())

    # def test_type_double_card_two_sets(self):
    #     xcard = self.load_card(self.huntmaster_json, "Huntmaster of the Fells", set_abbr='FOO')
    #     xcard2 = self.load_card(self.ravager_json, "Ravager of the Fells", loadhelper=False, set_abbr='FOO')
    #     card = self.load_card(self.huntmaster_json, "Huntmaster of the Fells", loadhelper=False, set_abbr='BAR')
    #     card2 = self.load_card(self.ravager_json, "Ravager of the Fells", loadhelper=False, set_abbr='BAR')
    #     pcard = card.physicalcard
    #     self.assertEquals(pcard.layout, pcard.DOUBLE)
    #     pcard2 = card.physicalcard
    #     self.assertEquals(pcard2.layout, pcard.DOUBLE)
    #     self.assertEquals(pcard, pcard2)

    #     self.assertEquals(card.name, 'Huntmaster of the Fells')
    #     self.assertEquals(card.cardposition, card.FRONT)
    #     self.assertEquals(card2.name, 'Ravager of the Fells')
    #     self.assertEquals(card2.cardposition, card.BACK)

    #     hunt = card.card_set.all().first()
    #     ravager = card2.card_set.all().first()

    #     self.assertEquals(hunt, ravager.get_double_faced_card())
    #     self.assertEquals(ravager, hunt.get_double_faced_card())


    def test_leveler_card(self):
        card = self.load_card(self.ikiral_outrider_json, "Ikiral Outrider")
        pcard = card.physicalcard
        self.assertEquals(pcard.layout, pcard.LEVELER)


