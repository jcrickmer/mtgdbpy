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

out = sys.stdout

format_hashtags = {'Standard': '#mtgstandard',
                   'Modern': '#mtgmodern',
                   'Commander': '#mtgcommander #edh',
                   'TinyLeaders': '#mtgtiny'
                   }


class Command(BaseCommand):
    #args = '<poll_id poll_id ...>'
    help = 'Generate some generic tweets to get people battling.'

    def handle(self, *args, **options):
        cur_formats = Format.objects.filter(start_date__lte=datetime.today(), end_date__gte=datetime.today()).order_by('format')
        use_bitly = settings.USE_BITLY
        # connect to bitly
        conn_bitly = bitly_api.Connection(access_token=settings.BITLY_ACCESS_TOKEN)

        for counter in range(0, 1):
            format_count = len(list(cur_formats))
            format_index = int(random.random() * format_count)
            cur_format = cur_formats[format_index]

            spreds = []
            spred = SearchPredicate()
            spred.term = 'format'
            spred.value = cur_format.id
            spreds.append(spred)
            sd = SortDirective()
            sd.term = 'cardrating'
            sd.direction = sd.DESC
            sd.crs_format_id = cur_format.id
            spreds.append(sd)
            card_list = Card.playables.search(spreds)

            rand_index = 5 + int(random.random() * 90)
            comp_index = int(random.random() * 10) - 5 + rand_index
            if comp_index == rand_index:
                comp_index = comp_index + 1

            first_card = card_list[rand_index]
            comp_card = card_list[comp_index]

            comp_word = 'worse'
            if comp_index > rand_index:
                comp_word = 'better'

            url_raw = 'http://card.ninja/cards/battle/' + cur_format.formatname + '/?bcid=' + str(first_card.basecard.id)
            url_raw = url_raw + '&utm_source=Social&utm_medium=post&utm_campaign=calltobattle'
            if use_bitly:
                bitly = conn_bitly.shorten(url_raw)
            else:
                bitly = {"url": url_raw}

            tweet = '{} rated {} than {} in {}. {} #MTG #CardBattle'.format(
                first_card.basecard.name,
                comp_word,
                comp_card.basecard.name,
                format_hashtags[
                    cur_format.formatname],
                bitly['url'])
            out.write(tweet + "\n[[" + str(url_raw) + "]]\n\n")
            out.write("first Card muid: " + str(first_card.multiverseid) + "\n")
            out.write("comp Card muid: " + str(comp_card.multiverseid) + "\n")
            im1_file_path = settings.STATIC_ROOT_CARD_IMAGES + '/' + str(first_card.multiverseid) + '.jpg'
            im2_file_path = settings.STATIC_ROOT_CARD_IMAGES + '/' + str(comp_card.multiverseid) + '.jpg'
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
                m.update(tweet)
                output_filename = m.hexdigest() + '.jpg'
                output_full_filename = settings.DYNAMIC_IMAGE_FILE_ROOT + '/' + output_filename
                im_result.save(output_full_filename, 'JPEG', quality=88)
                out.write('Image: {}\n'.format(output_full_filename))
                # 'd' will need to be setup in Apache, pointing to settings.DYNAMIC_IMAGE_FILE_ROOT
                out.write('Image URL: http://card.ninja/d/{}\n'.format(output_filename))
            except IOError as ioe:
                out.write("Oh no. " + str(ioe))
