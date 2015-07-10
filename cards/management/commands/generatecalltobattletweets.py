# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from cards.models import Card, CardManager, SearchPredicate, SortDirective
from cards.models import CardRating
from cards.models import Format
from cards.models import FormatBasecard
from cards.models import PhysicalCard
from cards.models import BaseCard

import random
import logging

from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings

import bitly_api
import hashlib

import sys
import os
from PIL import Image
from PIL import ImageFilter, ImageOps


from twython import Twython

out = sys.stdout

format_hashtags = {'Standard': '#mtgstandard',
                   'Origins': '#MTGOrigins',
                   'Modern': '#mtgmodern',
                   'Commander': '#mtgcommander #edh',
                   'TinyLeaders': '#mtgtiny'
                   }


class Command(BaseCommand):
    #args = '<poll_id poll_id ...>'
    help = 'Generate some generic tweets to get people battling.'

    def handle(self, *args, **options):
        cur_formats = Format.objects.filter(start_date__lte=datetime.today(), end_date__gte=datetime.today()).order_by('format')

        #rand_card_gen = BaseCardRandomizer()
        #rand_card_gen = MM2CardRandomizer()
        rand_card_gen = OriginsCardRandomizer()
        #rand_card_gen = RatedCardRandomizer()

        cur_format = rand_card_gen.get_format()
        first_card = rand_card_gen.get_first_card()
        comp_card = rand_card_gen.get_second_card()

        tweet = rand_card_gen.produce_tweet()

        out.write(tweet + "\n")
        #out.write("first Card muid: " + str(first_card.multiverseid) + "\n")
        #out.write("comp Card muid: " + str(comp_card.multiverseid) + "\n")
        image_locs = self.produce_image(first_card, comp_card)
        for key in image_locs.keys():
            out.write("Image {}: {}\n".format(key, image_locs[key]))

        if True:
            self.send_tweet(tweet, image_locs['filename'])

    def produce_image(self, card_one, card_two):
        result = dict()
        im1_file_path = settings.STATIC_ROOT_CARD_IMAGES + '/' + str(card_one.multiverseid) + '.jpg'
        im2_file_path = settings.STATIC_ROOT_CARD_IMAGES + '/' + str(card_two.multiverseid) + '.jpg'
        mask_file_path = settings.STATIC_ROOT_CN + '/' + 'card_mask.png'
        logo_file_path = settings.STATIC_ROOT_CN + '/' + 'cardninja_glow.png'
        try:
            mask = Image.open(mask_file_path).convert('L')

            logo = Image.open(logo_file_path)
            logo = logo.resize((int(logo.size[0] * .75), int(logo.size[1] * .75)), resample=Image.BICUBIC)

            im1_card = Image.open(im1_file_path)
            if im1_card.mode != 'RGBA':
                im1_card = im1_card.convert('RGBA')
                im1_card = ImageOps.fit(im1_card, mask.size, centering=(0.5, 0.5))
                im1_card.putalpha(mask)
            im2_card = Image.open(im2_file_path)
            if im2_card.mode != 'RGBA':
                im2_card = im2_card.convert('RGBA')
                im2_card = ImageOps.fit(im2_card, mask.size, centering=(0.5, 0.5))
                im2_card.putalpha(mask)

            im_result = Image.new('RGBA', (546, 340))
            back_crop = im1_card.crop((30, 60, 200, 140))
            back_crop = back_crop.resize((int(170 * 3.5), int(120 * 3.5)), resample=Image.BICUBIC)
            back_crop = back_crop.filter(ImageFilter.GaussianBlur(radius=5))

            im1_rot = im1_card.rotate(9, resample=Image.BICUBIC, expand=True)
            im2_rot = im2_card.rotate(-9, resample=Image.BICUBIC, expand=True)
            im1_rot_a = im1_rot.filter(ImageFilter.GaussianBlur(radius=2))
            im2_rot_a = im2_rot.filter(ImageFilter.GaussianBlur(radius=2))

            im_result.paste(back_crop, (0, 0))
            im_result.paste(im2_rot_a, (235, 0), im2_rot_a)
            im_result.paste(im2_rot, (235, 0), im2_rot)
            im_result.paste(im1_rot_a, (40, 0), im1_rot_a)
            im_result.paste(im1_rot, (40, 0), im1_rot)
            im_result.paste(logo, (im_result.size[0] - 5 - logo.size[0], im_result.size[1] - 5 - logo.size[1],), logo)

            m = hashlib.md5()
            m.update('{}-{}'.format(card_one.basecard.filing_name, card_two.basecard.filing_name))
            output_filename = m.hexdigest() + '.jpg'
            output_full_filename = settings.DYNAMIC_IMAGE_FILE_ROOT + '/' + output_filename
            im_result.save(output_full_filename, 'JPEG', quality=88)
            # 'd' will need to be setup in Apache, pointing to settings.DYNAMIC_IMAGE_FILE_ROOT
            result = {'filename': output_full_filename,
                      'url': 'http://card.ninja/d/{}'.format(output_filename)}
        except IOError as ioe:
            out.write("Oh no. " + str(ioe))
        return result

    def send_tweet(self, tweet, media_filename):
        # these values came from the auth = twitter.get_authentication_tokens() call below.
        #twitter = Twython(APP_KEY, APP_SECRET)
        #auth = twitter.get_authentication_tokens()
        # for key in auth.keys():
        #    sys.stderr.write("oauth {} = '{}'\n".format(key, auth[key]))
        # https://twython.readthedocs.org/en/latest/usage/starting_out.html#starting-out
        # Now, go to the URL and complete the process. Get the PIN number and put that into the get_authorized_tokens call below.
        #twitter_li = Twython(APP_KEY, APP_SECRET, '8gDs7j68yJZirbQkrd32Cj2cYzILyR68', 'EX4moMI98JrYaB28mOIHU4ZWag7nCVfT')
        #final_step = twitter_li.get_authorized_tokens('7437869')
        # for key in final_step.keys():
        #    sys.stderr.write("oauth {} = '{}'\n".format(key, final_step[key]))
        ##
        # oauth oauth_token_secret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        # oauth user_id = '2222222222'
        # oauth oauth_token = '2222222222-mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm'
        # oauth screen_name = 'dev327364652'

        twitter_act = Twython(settings.APP_KEY, settings.APP_SECRET, settings.OAUTH_TOKEN, settings.OAUTH_TOKEN_SECRET)

        # twitter_act.update_status(status=tweet)
        photo = open(media_filename, 'rb')
        twitter_act.update_status_with_media(status=tweet, media=photo)

        pass


class BaseCardRandomizer():

    def __init__(self):
        self.tweet = ''
        cur_formats = Format.objects.filter(start_date__lte=datetime.today(), end_date__gte=datetime.today()).order_by('format')
        self.cur_format = random.choice(cur_formats)

        for counter in range(0, 1):
            spreds = []
            spred = SearchPredicate()
            spred.term = 'format'
            spred.value = self.cur_format.id
            spreds.append(spred)
            sd = SortDirective()
            sd.term = 'cardrating'
            sd.direction = sd.DESC
            sd.crs_format_id = self.cur_format.id
            spreds.append(sd)
            card_list = Card.playables.search(spreds)

            rand_index = 5 + int(random.random() * 90)
            comp_index = int(random.random() * 10) - 5 + rand_index
            if comp_index == rand_index:
                comp_index = comp_index + 1

            self.first_card = card_list[rand_index]
            self.comp_card = card_list[comp_index]

    ''' Returns the tweet.
    '''

    def produce_tweet(self):
        self.tweet = ''

        fc_cr = CardRating.objects.filter(physicalcard=self.first_card.basecard.physicalcard, format=self.cur_format, test__id=1).first()
        cc_cr = CardRating.objects.filter(physicalcard=self.comp_card.basecard.physicalcard, format=self.cur_format, test__id=1).first()

        comp_word = 'worse'
        if fc_cr.mu > cc_cr.mu:
            comp_word = 'better'

        url_raw = 'http://card.ninja/cards/battle/' + self.cur_format.formatname + '/?bcid=' + str(self.first_card.basecard.id)
        url_raw = url_raw + '&utm_source=Social&utm_medium=post&utm_campaign=calltobattle'

        use_bitly = settings.USE_BITLY
        # connect to bitly
        conn_bitly = bitly_api.Connection(access_token=settings.BITLY_ACCESS_TOKEN)

        bitly = dict()
        if use_bitly:
            bitly = conn_bitly.shorten(url_raw)
        else:
            bitly = {"url": url_raw}

        self.tweet = '{} rated {} than {} in {}. {}'.format(
            self.first_card.basecard.name,
            comp_word,
            self.comp_card.basecard.name,
            format_hashtags[self.cur_format.formatname],
            bitly['url'])

        return self.tweet

    ''' Returns a Format object. Both first_card and second_card should be members of this Format.
    '''

    def get_format(self):
        return self.cur_format

    ''' Returns a Card object.
    '''

    def get_first_card(self):
        return self.first_card

    ''' Returns a Card object.
    '''

    def get_second_card(self):
        return self.comp_card


class RatedCardRandomizer(BaseCardRandomizer):

    def __init__(self):
        self.tweet = ''
        cur_formats = Format.objects.filter(start_date__lte=datetime.today(), end_date__gte=datetime.today()).order_by('format')
        self.cur_format = random.choice(cur_formats)

        for counter in range(0, 1):
            spreds = []
            spred = SearchPredicate()
            spred.term = 'format'
            spred.value = self.cur_format.id
            spreds.append(spred)
            spred_cr = SearchPredicate()
            spred_cr.term = 'cardrating'
            spred_cr.operator = SearchPredicate.GREATER_THAN
            spred_cr.value = 500.0
            spreds.append(spred_cr)
            sd = SortDirective()
            sd.term = 'cardrating'
            sd.direction = sd.DESC
            sd.crs_format_id = self.cur_format.id
            spreds.append(sd)
            card_list = Card.playables.search(spreds)

            rand_index = 5 + int(random.random() * 90)
            comp_index = int(random.random() * 10) - 5 + rand_index
            if comp_index == rand_index:
                comp_index = comp_index + 1

            self.first_card = card_list[rand_index]
            self.comp_card = card_list[comp_index]


class OriginsCardRandomizer(BaseCardRandomizer):

    def __init__(self):
        cur_formats = Format.objects.filter(
            formatname='Origins',
            start_date__lte=datetime.today(),
            end_date__gte=datetime.today()).order_by('format')
        format_count = len(list(cur_formats))
        format_index = int(random.random() * format_count)
        self.cur_format = cur_formats[format_index]

        #ori_cards = Card.objects.filter(expansionset_id=187)
        #ori_card_names = [x.basecard.name for x in ori_cards]
        
        spreds = []
        spred = SearchPredicate()
        spred.term = 'format'
        spred.value = self.cur_format.id
        spreds.append(spred)
        #spred_n = SearchPredicate()
        #spred_n.term = 'name'
        #spred_n.value = random.choice(ori_card_names)
        #spreds.append(spred_n)
        sd = SortDirective()
        sd.term = 'cardrating'
        sd.direction = sd.DESC
        sd.crs_format_id = self.cur_format.id
        spreds.append(sd)
        card_list = Card.playables.search(spreds)

        self.first_card = card_list[0]
        fc_cr = CardRating.objects.filter(physicalcard=self.first_card.basecard.physicalcard, format=self.cur_format, test__id=1).first()
        #sys.stderr.write("first card is {}\n".format(self.first_card.basecard.name))
        #sys.stderr.write("first card rating sigma {}, mu {} \n".format(fc_cr.sigma, fc_cr.mu))

        spreds2 = []
        spred = SearchPredicate()
        spred.term = 'format'
        spred.value = self.cur_format.id
        spreds2.append(spred)

        spred_u = SearchPredicate()
        spred_u.term = 'cardrating'
        spred_u.operator = SearchPredicate.LESS_THAN
        spred_u.value = 20.0 * (fc_cr.mu + (1.0 * fc_cr.sigma))
        spreds2.append(spred_u)

        spred_l = SearchPredicate()
        spred_l.term = 'cardrating'
        spred_l.operator = SearchPredicate.GREATER_THAN
        spred_l.value = 20.0 * (fc_cr.mu - (1.0 * fc_cr.sigma))
        spreds2.append(spred_l)

        spred_n = SearchPredicate()
        spred_n.term = 'name'
        spred_n.negative = True
        spred_n.value = self.first_card.basecard.name
        spreds2.append(spred_n)
        #sys.stderr.write("spreds2 is {}\n".format(str(spreds2)))
        for sp in spreds2:
            #sys.stderr.write("spreds2: {} {} {}\n".format(sp.term, sp.operator, sp.value))
            pass
        card_list2 = Card.playables.search(spreds2)
        act_list = list()
        for cccc in card_list2:
            #sys.stderr.write("cccc is {}\n".format(cccc.basecard.filing_name))
            act_list.append(cccc)
        self.comp_card = random.choice(act_list)

    def produce_tweet(self):
        self.tweet = ''

        fc_cr = CardRating.objects.filter(physicalcard=self.first_card.basecard.physicalcard, format=self.cur_format, test__id=1).first()
        cc_cr = CardRating.objects.filter(physicalcard=self.comp_card.basecard.physicalcard, format=self.cur_format, test__id=1).first()

        comp_word = 'worse'
        if fc_cr.mu > cc_cr.mu:
            comp_word = 'better'

        url_raw = 'http://card.ninja/cards/battle/' + self.cur_format.formatname + '/?bcid=' + str(self.first_card.basecard.id)
        url_raw = url_raw + '&utm_source=Social&utm_medium=post&utm_campaign=calltobattle'

        use_bitly = settings.USE_BITLY
        # connect to bitly
        conn_bitly = bitly_api.Connection(access_token=settings.BITLY_ACCESS_TOKEN)

        bitly = dict()
        if use_bitly:
            bitly = conn_bitly.shorten(url_raw)
        else:
            bitly = {"url": url_raw}

        self.tweet = '{} rated {} than {} in #MTGOrigins limited'.format(
                self.first_card.basecard.name,
                comp_word,
                self.comp_card.basecard.name,
                bitly['url'])

        return self.tweet

            
class MM2CardRandomizer(BaseCardRandomizer):

    def __init__(self):
        cur_formats = Format.objects.filter(
            formatname='Modern',
            start_date__lte=datetime.today(),
            end_date__gte=datetime.today()).order_by('format')
        format_count = len(list(cur_formats))
        format_index = int(random.random() * format_count)
        self.cur_format = cur_formats[format_index]

        mm2_card_names = ["Sundering Vitae",
                          "Darksteel Citadel",
                          "Wayfarer's Bauble",
                          "Tumble Magnet",
                          "Sphere of the Suns",
                          "Skyreach Manta",
                          "Sickleslicer",
                          "Runed Servitor",
                          "Precursor Golem",
                          "Myr Enforcer",
                          "Long-Forgotten Gohei",
                          "Lodestone Myr",
                          "Evolving Wilds",
                          "Lodestone Golem",
                          "Kitesail",
                          "Wrecking Ball",
                          "Gust-Skimmer",
                          "Vengeful Rebirth",
                          "Glint Hawk Idol",
                          "Frogmite",
                          "Sigil Blessing",
                          "Flayer Husk",
                          "Expedition Map",
                          "Shrewd Hatchling",
                          "Everflowing Chalice",
                          "Selesnya Guildmage",
                          "Darksteel Axe",
                          "Savage Twister",
                          "Culling Dais",
                          "Restless Apparition",
                          "Copper Carapace",
                          "Plaxcaster Frogling",
                          "Pillory of the Sleepless",
                          "Chimeric Mass",
                          "Necrogenesis",
                          "Cathodion",
                          "Lorescale Coatl",
                          "Hearthfire Hobgoblin",
                          "Glassdust Hulk",
                          "Blinding Souleater",
                          "Ethercaste Knight",
                          "Electrolyze",
                          "Alloy Myr",
                          "Drooling Groodion",
                          "Ulamog's Crusher",
                          "Waking Nightmare",
                          "Wings of Velis Vel",
                          "Vampire Outcasts",
                          "Water Servant",
                          "Dimir Guildmage",
                          "Vigean Graftmage",
                          "Boros Swiftblade",
                          "Spread the Sickness",
                          "Vapor Snag",
                          "Ashenmoor Gouger",
                          "Agony Warp",
                          "Sign in Blood",
                          "Thrummingbird",
                          "Sickle Ripper",
                          "Thoughtcast",
                          "Shrivel",
                          "Tezzeret's Gambit",
                          "Scuttling Death",
                          "Telling Time",
                          "Scavenger Drake",
                          "Reassembling Skeleton",
                          "Wolfbriar Elemental",
                          "Vines of Vastwood",
                          "Surrakar Spellblade",
                          "Puppeteer Clique",
                          "Tukatongue Thallid",
                          "Stoic Rebuttal",
                          "Plagued Rusalka",
                          "Steady Progress",
                          "Thrive",
                          "Sylvan Bounty",
                          "Midnight Banshee",
                          "Somber Hoverguard",
                          "Simic Initiate",
                          "Repeal",
                          "Scute Mob",
                          "Qumulox",
                          "Instill Infection",
                          "Scatter the Seeds",
                          "Novijen Sages",
                          "Grim Affliction",
                          "Root-Kin Ally",
                          "Rampant Growth",
                          "Narcolepsy",
                          "Ghostly Changeling",
                          "Plummet",
                          "Mana Leak",
                          "Pelakka Wurm",
                          "Duskhunter Bat",
                          "Inexorable Tide",
                          "Overwhelming Stampede",
                          "Devouring Greed",
                          "Deathmark",
                          "Overwhelm",
                          "Helium Squirter",
                          "Death Denied",
                          "Mutagenic Growth",
                          "Guile",
                          "Matca Rioters",
                          "Flashfreeze",
                          "Kavu Primarch",
                          "Daggerclaw Imp",
                          "Bone Splinters",
                          "Faerie Mechanist",
                          "Karplusan Strider",
                          "Cloud Elemental",
                          "Gnarlid Pack",
                          "Cytoplast Root-Kin",
                          "Commune with Nature",
                          "Argent Sphinx",
                          "Terashi's Grasp",
                          "Air Servant",
                          "Taj-Nar Swordsmith",
                          "Bestial Menace",
                          "Æthersnipe",
                          "Sunspear Shikari",
                          "Aquastrand Spider",
                          "Sunlance",
                          "Algae Gharial",
                          "Spectral Procession",
                          "Wrap in Flames",
                          "Worldheart Phoenix",
                          "Skyhunter Skirmisher",
                          "Viashino Slaughtermaster",
                          "Raise the Alarm",
                          "Tribal Flames",
                          "Otherworldly Journey",
                          "Thunderblust",
                          "Spitebellows",
                          "Oblivion Ring",
                          "Spikeshot Elder",
                          "Myrsmith",
                          "Soulbright Flamekin",
                          "Smokebraider",
                          "Smash to Smithereens",
                          "Skarrgan Firebird",
                          "Moonlit Strider",
                          "Inner-Flame Igniter",
                          "Incandescent Soulstoke",
                          "Hellkite Charger",
                          "Mighty Leap",
                          "Gut Shot",
                          "Kor Duelist",
                          "Gorehorn Minotaurs",
                          "Goblin War Paint",
                          "Kami of Ancient Law",
                          "Fiery Fall",
                          "Fortify",
                          "Dragonsoul Knight",
                          "Combust",
                          "Court Homunculus",
                          "Burst Lightning",
                          "Conclave Phalanx",
                          "Brute Force",
                          "Celestial Purge",
                          "Bloodshot Trainee",
                          "Battlegrace Angel",
                          "Blood Ogre",
                          "Arrest",
                          "Blades of Velis Vel",
                          "Apostle's Blessing",
                          "Banefire",
                          "Ant Queen",
                          "Nobilis of War",
                          "Niv-Mizzet, the Firemind",
                          "Mirror Entity",
                          "Wilt-Leaf Liege",
                          "Elesh Norn, Grand Cenobite",
                          "Comet Storm",
                          "Sunforger",
                          "Simic Growth Chamber",
                          "Orzhov Basilica",
                          "Mortarpod",
                          "Dread Drone",
                          "Izzet Boilerworks",
                          "Golgari Rot Farm",
                          "Selesnya Sanctuary",
                          "Rakdos Carnarium",
                          "Boros Garrison",
                          "Gruul Turf",
                          "Mystic Snake",
                          "Dimir Aqueduct",
                          "Azorius Chancery",
                          "Necroskitter",
                          "Remand",
                          "Tezzeret the Seeker",
                          "Mulldrifter",
                          "Kiki-Jiki, Mirror Breaker",
                          "Scion of the Wild",
                          "Nest Invader",
                          "Ghost Council of Orzhova",
                          "Nameless Inversion",
                          "Thief of Hope",
                          "Waxmane Baku",
                          "Hikari, Twilight Guardian",
                          "Wildfire",
                          "Blinkmoth Nexus",
                          "Creakwood Liege",
                          "Horde of Notions",
                          "Indomitable Archangel",
                          "Surgical Extraction",
                          "Dispatch",
                          "Leyline of Sanctity",
                          "Etched Oracle",
                          "Ulamog, the Infinite Gyre",
                          "Etched Monstrosity",
                          "Kozilek's Predator",
                          "All Suns' Dawn",
                          "Eye of Ugin",
                          "Eldrazi Temple",
                          "Shadowmage Infiltrator",
                          "Artisan of Kozilek",
                          "Hurkyl's Recall",
                          "Apocalypse Hydra",
                          "Iona, Shield of Emeria",
                          "All Is Dust",
                          "Fulminator Mage",
                          "Lightning Bolt",
                          "Bitterblossom",
                          "Swans of Bryn Argoll",
                          "Kozilek, Butcher of Truth",
                          "Mirran Crusader",
                          "Primeval Titan",
                          "Cranial Plating",
                          "Rusted Relic",
                          "Bloodthrone Vampire",
                          "Endrek Sahr, Master Breeder",
                          "Dismember",
                          "Stormblood Berserker",
                          "Vampire Lacerator",
                          "Goblin Fireslinger",
                          "Daybreak Coronet",
                          "Spellskite",
                          "Noble Hierarch",
                          "Cryptic Command",
                          "Profane Command",
                          "Mox Opal",
                          "Splinter Twin",
                          "Dark Confidant",
                          "Vendilion Clique",
                          "Karn Liberated",
                          "Tarmogoyf",
                          "Emrakul, the Aeons Torn",
                          "Etched Champion"]

        spreds = []
        spred = SearchPredicate()
        spred.term = 'format'
        spred.value = self.cur_format.id
        spreds.append(spred)
        spred_n = SearchPredicate()
        spred_n.term = 'name'
        spred_n.value = random.choice(mm2_card_names)
        spreds.append(spred_n)
        sd = SortDirective()
        sd.term = 'cardrating'
        sd.direction = sd.DESC
        sd.crs_format_id = self.cur_format.id
        spreds.append(sd)
        card_list = Card.playables.search(spreds)

        self.first_card = card_list[0]
        fc_cr = CardRating.objects.filter(physicalcard=self.first_card.basecard.physicalcard, format=self.cur_format, test__id=1).first()
        #sys.stderr.write("first card is {}\n".format(self.first_card.basecard.name))
        #sys.stderr.write("first card rating sigma {}, mu {} \n".format(fc_cr.sigma, fc_cr.mu))

        spreds2 = []
        spred = SearchPredicate()
        spred.term = 'format'
        spred.value = self.cur_format.id
        spreds2.append(spred)

        spred_u = SearchPredicate()
        spred_u.term = 'cardrating'
        spred_u.operator = SearchPredicate.LESS_THAN
        spred_u.value = 20.0 * (fc_cr.mu + (1.0 * fc_cr.sigma))
        spreds2.append(spred_u)

        spred_l = SearchPredicate()
        spred_l.term = 'cardrating'
        spred_l.operator = SearchPredicate.GREATER_THAN
        spred_l.value = 20.0 * (fc_cr.mu - (1.0 * fc_cr.sigma))
        spreds2.append(spred_l)

        spred_n = SearchPredicate()
        spred_n.term = 'name'
        spred_n.negative = True
        spred_n.value = self.first_card.basecard.name
        spreds2.append(spred_n)
        #sys.stderr.write("spreds2 is {}\n".format(str(spreds2)))
        for sp in spreds2:
            #sys.stderr.write("spreds2: {} {} {}\n".format(sp.term, sp.operator, sp.value))
            pass
        card_list2 = Card.playables.search(spreds2)
        act_list = list()
        for cccc in card_list2:
            #sys.stderr.write("cccc is {}\n".format(cccc.basecard.filing_name))
            act_list.append(cccc)
        self.comp_card = random.choice(act_list)

    def produce_tweet(self):
        self.tweet = ''

        fc_cr = CardRating.objects.filter(physicalcard=self.first_card.basecard.physicalcard, format=self.cur_format, test__id=1).first()
        cc_cr = CardRating.objects.filter(physicalcard=self.comp_card.basecard.physicalcard, format=self.cur_format, test__id=1).first()

        comp_word = 'worse'
        if fc_cr.mu > cc_cr.mu:
            comp_word = 'better'

        url_raw = 'http://card.ninja/cards/battle/' + self.cur_format.formatname + '/?bcid=' + str(self.first_card.basecard.id)
        url_raw = url_raw + '&utm_source=Social&utm_medium=post&utm_campaign=calltobattle'

        use_bitly = settings.USE_BITLY
        # connect to bitly
        conn_bitly = bitly_api.Connection(access_token=settings.BITLY_ACCESS_TOKEN)

        bitly = dict()
        if use_bitly:
            bitly = conn_bitly.shorten(url_raw)
        else:
            bitly = {"url": url_raw}

        if random.random() > 0.05:
            self.tweet = '{} rated {} than {}. {} #MTGMM2015'.format(
                self.first_card.basecard.name,
                comp_word,
                self.comp_card.basecard.name,
                bitly['url'])
        else:
            self.tweet = '{} rated {} than {} in {}. {} #MTGMM2015'.format(
                self.first_card.basecard.name,
                comp_word,
                self.comp_card.basecard.name,
                format_hashtags[self.cur_format.formatname],
                bitly['url'])

        return self.tweet
