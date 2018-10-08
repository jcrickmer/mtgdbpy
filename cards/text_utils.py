# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys
from django.db import models
from django.core.exceptions import ValidationError

from cards.view_utils import convertSymbolsToHTML
from django.utils.safestring import mark_safe

import logging
from operator import itemgetter

from django.core.cache import cache

import re


def filing_string(input):
    result = input
    result = filing_string_rule_1(input)
    result = filing_string_rule_2(result)
    result = filing_string_rule_3(result)
    result = filing_string_rule_4(result)
    result = filing_string_rule_5(result)
    result = filing_string_rule_6(result)
    result = filing_string_rule_7(result)
    result = filing_string_rule_8(result)
    result = filing_string_rule_9(result)
    result = filing_string_rule_10(result)
    result = filing_string_rule_11(result)
    result = filing_string_rule_12(result)
    result = filing_string_rule_13(result)
    # Putting Rule 16 before Rule 14 since comma can be used in numbers and it is easier to process this first.
    result = filing_string_rule_16(result)
    result = filing_string_rule_14(result)
    result = filing_string_rule_15(result)
    result = result.strip()
    if len(result) == 0:
        result = 'blank'
    return result

# Rule 1 - General Principle
#
# This is standard alphetical order, which computers are good at. But,
# let's lowercase everything to make sure that we are playing in the same space.


def filing_string_rule_1(input):
    return input.lower()

# Rule 2 - Treat modified letters like their equivalents in the
# English alphabet. Ignore diacritical marks and modifications of
# recognizable English letters


def filing_string_rule_2(input):
    result = input
    result = result.replace('\u00c0', 'a')  # LATIN CAPITAL LETTER A WITH GRAVE
    result = result.replace('\u00c1', 'a')  # LATIN CAPITAL LETTER A WITH ACUTE
    result = result.replace('\u00c2', 'a')  # LATIN CAPITAL LETTER A WITH CIRCUMFLEX
    result = result.replace('\u00c3', 'a')  # LATIN CAPITAL LETTER A WITH TILDE
    result = result.replace('\u00c4', 'a')  # LATIN CAPITAL LETTER A WITH DIAERESIS
    result = result.replace('\u00c5', 'a')  # LATIN CAPITAL LETTER A WITH RING ABOVE
    result = result.replace('\u00c6', 'ae')  # LATIN CAPITAL LETTER AE
    result = result.replace('\u00c7', 'c')  # LATIN CAPITAL LETTER C WITH CEDILLA
    result = result.replace('\u00c8', 'e')  # LATIN CAPITAL LETTER E WITH GRAVE
    result = result.replace('\u00c9', 'e')  # LATIN CAPITAL LETTER E WITH ACUTE
    result = result.replace('\u00ca', 'e')  # LATIN CAPITAL LETTER E WITH CIRCUMFLEX
    result = result.replace('\u00cb', 'e')  # LATIN CAPITAL LETTER E WITH DIAERESIS
    result = result.replace('\u00cc', 'i')  # LATIN CAPITAL LETTER I WITH GRAVE
    result = result.replace('\u00cd', 'i')  # LATIN CAPITAL LETTER I WITH ACUTE
    result = result.replace('\u00ce', 'i')  # LATIN CAPITAL LETTER I WITH CIRCUMFLEX
    result = result.replace('\u00cf', 'i')  # LATIN CAPITAL LETTER I WITH DIAERESIS
    result = result.replace('\u00d0', 'd')  # LATIN CAPITAL LETTER ETH
    result = result.replace('\u00d1', 'n')  # LATIN CAPITAL LETTER N WITH TILDE
    result = result.replace('\u00d2', 'o')  # LATIN CAPITAL LETTER O WITH GRAVE
    result = result.replace('\u00d3', 'o')  # LATIN CAPITAL LETTER O WITH ACUTE
    result = result.replace('\u00d4', 'o')  # LATIN CAPITAL LETTER O WITH CIRCUMFLEX
    result = result.replace('\u00d5', 'o')  # LATIN CAPITAL LETTER O WITH TILDE
    result = result.replace('\u00d6', 'o')  # LATIN CAPITAL LETTER O WITH DIAERESIS
    result = result.replace('\u00d7', ' ')  # MULTIPLICATION SIGN
    result = result.replace('\u00d8', 'o')  # LATIN CAPITAL LETTER O WITH STROKE
    result = result.replace('\u00d9', 'u')  # LATIN CAPITAL LETTER U WITH GRAVE
    result = result.replace('\u00da', 'u')  # LATIN CAPITAL LETTER U WITH ACUTE
    result = result.replace('\u00db', 'u')  # LATIN CAPITAL LETTER U WITH CIRCUMFLEX
    result = result.replace('\u00dc', 'u')  # LATIN CAPITAL LETTER U WITH DIAERESIS
    result = result.replace('\u00dd', 'y')  # LATIN CAPITAL LETTER Y WITH ACUTE
    result = result.replace('\u00de', 'th')  # LATIN CAPITAL LETTER THORN
    result = result.replace('\u00df', 's')  # LATIN SMALL LETTER SHARP S
    result = result.replace('\u00e0', 'a')  # LATIN SMALL LETTER A WITH GRAVE
    result = result.replace('\u00e1', 'a')  # LATIN SMALL LETTER A WITH ACUTE
    result = result.replace('\u00e2', 'a')  # LATIN SMALL LETTER A WITH CIRCUMFLEX
    result = result.replace('\u00e3', 'a')  # LATIN SMALL LETTER A WITH TILDE
    result = result.replace('\u00e4', 'a')  # LATIN SMALL LETTER A WITH DIAERESIS
    result = result.replace('\u00e5', 'a')  # LATIN SMALL LETTER A WITH RING ABOVE
    result = result.replace('\u00e6', 'ae')  # LATIN SMALL LETTER AE
    result = result.replace('\u00e7', 'c')  # LATIN SMALL LETTER C WITH CEDILLA
    result = result.replace('\u00e8', 'e')  # LATIN SMALL LETTER E WITH GRAVE
    result = result.replace('\u00e9', 'e')  # LATIN SMALL LETTER E WITH ACUTE
    result = result.replace('\u00ea', 'e')  # LATIN SMALL LETTER E WITH CIRCUMFLEX
    result = result.replace('\u00eb', 'e')  # LATIN SMALL LETTER E WITH DIAERESIS
    result = result.replace('\u00ec', 'i')  # LATIN SMALL LETTER I WITH GRAVE
    result = result.replace('\u00ed', 'i')  # LATIN SMALL LETTER I WITH ACUTE
    result = result.replace('\u00ee', 'i')  # LATIN SMALL LETTER I WITH CIRCUMFLEX
    result = result.replace('\u00ef', 'i')  # LATIN SMALL LETTER I WITH DIAERESIS
    result = result.replace('\u00f0', 'd')  # LATIN SMALL LETTER ETH
    result = result.replace('\u00f1', 'n')  # LATIN SMALL LETTER N WITH TILDE
    result = result.replace('\u00f2', 'o')  # LATIN SMALL LETTER O WITH GRAVE
    result = result.replace('\u00f3', 'o')  # LATIN SMALL LETTER O WITH ACUTE
    result = result.replace('\u00f4', 'o')  # LATIN SMALL LETTER O WITH CIRCUMFLEX
    result = result.replace('\u00f5', 'o')  # LATIN SMALL LETTER O WITH TILDE
    result = result.replace('\u00f6', 'o')  # LATIN SMALL LETTER O WITH DIAERESIS
    result = result.replace('\u00f7', ' ')  # DIVISION SIGN
    result = result.replace('\u00f8', 'o')  # LATIN SMALL LETTER O WITH STROKE
    result = result.replace('\u00f9', 'u')  # LATIN SMALL LETTER U WITH GRAVE
    result = result.replace('\u00fa', 'u')  # LATIN SMALL LETTER U WITH ACUTE
    result = result.replace('\u00fb', 'u')  # LATIN SMALL LETTER U WITH CIRCUMFLEX
    result = result.replace('\u00fc', 'u')  # LATIN SMALL LETTER U WITH DIAERESIS
    result = result.replace('\u00fd', 'y')  # LATIN SMALL LETTER Y WITH ACUTE
    result = result.replace('\u00fe', 'th')  # LATIN SMALL LETTER THORN
    result = result.replace('\u00ff', 'y')  # LATIN SMALL LETTER Y WITH DIAERESIS
    result = result.replace('\u0100', 'a')  # LATIN CAPITAL LETTER A WITH MACRON
    result = result.replace('\u0101', 'a')  # LATIN SMALL LETTER A WITH MACRON
    result = result.replace('\u0102', 'a')  # LATIN CAPITAL LETTER A WITH BREVE
    result = result.replace('\u0103', 'a')  # LATIN SMALL LETTER A WITH BREVE
    result = result.replace('\u0104', 'a')  # LATIN CAPITAL LETTER A WITH OGONEK
    result = result.replace('\u0105', 'a')  # LATIN SMALL LETTER A WITH OGONEK
    result = result.replace('\u0106', 'c')  # LATIN CAPITAL LETTER C WITH ACUTE
    result = result.replace('\u0107', 'c')  # LATIN SMALL LETTER C WITH ACUTE
    result = result.replace('\u0108', 'c')  # LATIN CAPITAL LETTER C WITH CIRCUMFLEX
    result = result.replace('\u0109', 'c')  # LATIN SMALL LETTER C WITH CIRCUMFLEX
    result = result.replace('\u010a', 'c')  # LATIN CAPITAL LETTER C WITH DOT ABOVE
    result = result.replace('\u010b', 'c')  # LATIN SMALL LETTER C WITH DOT ABOVE
    result = result.replace('\u010c', 'c')  # LATIN CAPITAL LETTER C WITH CARON
    result = result.replace('\u010d', 'c')  # LATIN SMALL LETTER C WITH CARON
    result = result.replace('\u010e', 'd')  # LATIN CAPITAL LETTER D WITH CARON
    result = result.replace('\u010f', 'd')  # LATIN SMALL LETTER D WITH CARON
    result = result.replace('\u0110', 'd')  # LATIN CAPITAL LETTER D WITH STROKE
    result = result.replace('\u0111', 'd')  # LATIN SMALL LETTER D WITH STROKE
    result = result.replace('\u0112', 'e')  # LATIN CAPITAL LETTER E WITH MACRON
    result = result.replace('\u0113', 'e')  # LATIN SMALL LETTER E WITH MACRON
    result = result.replace('\u0114', 'e')  # LATIN CAPITAL LETTER E WITH BREVE
    result = result.replace('\u0115', 'e')  # LATIN SMALL LETTER E WITH BREVE
    result = result.replace('\u0116', 'e')  # LATIN CAPITAL LETTER E WITH DOT ABOVE
    result = result.replace('\u0117', 'e')  # LATIN SMALL LETTER E WITH DOT ABOVE
    result = result.replace('\u0118', 'e')  # LATIN CAPITAL LETTER E WITH OGONEK
    result = result.replace('\u0119', 'e')  # LATIN SMALL LETTER E WITH OGONEK
    result = result.replace('\u011a', 'e')  # LATIN CAPITAL LETTER E WITH CARON
    result = result.replace('\u011b', 'e')  # LATIN SMALL LETTER E WITH CARON
    result = result.replace('\u011c', 'g')  # LATIN CAPITAL LETTER G WITH CIRCUMFLEX
    result = result.replace('\u011d', 'g')  # LATIN SMALL LETTER G WITH CIRCUMFLEX
    result = result.replace('\u011e', 'g')  # LATIN CAPITAL LETTER G WITH BREVE
    result = result.replace('\u011f', 'g')  # LATIN SMALL LETTER G WITH BREVE
    result = result.replace('\u0120', 'g')  # LATIN CAPITAL LETTER G WITH DOT ABOVE
    result = result.replace('\u0121', 'g')  # LATIN SMALL LETTER G WITH DOT ABOVE
    result = result.replace('\u0122', 'g')  # LATIN CAPITAL LETTER G WITH CEDILLA
    result = result.replace('\u0123', 'g')  # LATIN SMALL LETTER G WITH CEDILLA
    result = result.replace('\u0124', 'h')  # LATIN CAPITAL LETTER H WITH CIRCUMFLEX
    result = result.replace('\u0125', 'h')  # LATIN SMALL LETTER H WITH CIRCUMFLEX
    result = result.replace('\u0126', 'h')  # LATIN CAPITAL LETTER H WITH STROKE
    result = result.replace('\u0127', 'h')  # LATIN SMALL LETTER H WITH STROKE
    result = result.replace('\u0128', 'i')  # LATIN CAPITAL LETTER I WITH TILDE
    result = result.replace('\u0129', 'i')  # LATIN SMALL LETTER I WITH TILDE
    result = result.replace('\u012a', 'i')  # LATIN CAPITAL LETTER I WITH MACRON
    result = result.replace('\u012b', 'i')  # LATIN SMALL LETTER I WITH MACRON
    result = result.replace('\u012c', 'i')  # LATIN CAPITAL LETTER I WITH BREVE
    result = result.replace('\u012d', 'i')  # LATIN SMALL LETTER I WITH BREVE
    result = result.replace('\u012e', 'i')  # LATIN CAPITAL LETTER I WITH OGONEK
    result = result.replace('\u012f', 'i')  # LATIN SMALL LETTER I WITH OGONEK
    result = result.replace('\u0130', 'i')  # LATIN CAPITAL LETTER I WITH DOT ABOVE
    result = result.replace('\u0131', 'i')  # LATIN SMALL LETTER DOTLESS I
    result = result.replace('\u0132', 'ij')  # LATIN CAPITAL LIGATURE IJ
    result = result.replace('\u0133', 'ij')  # LATIN SMALL LIGATURE IJ
    result = result.replace('\u0134', 'j')  # LATIN CAPITAL LETTER J WITH CIRCUMFLEX
    result = result.replace('\u0135', 'j')  # LATIN SMALL LETTER J WITH CIRCUMFLEX
    result = result.replace('\u0136', 'k')  # LATIN CAPITAL LETTER K WITH CEDILLA
    result = result.replace('\u0137', 'k')  # LATIN SMALL LETTER K WITH CEDILLA
    result = result.replace('\u0138', 'kr')  # LATIN SMALL LETTER KRA
    result = result.replace('\u0139', 'l')  # LATIN CAPITAL LETTER L WITH ACUTE
    result = result.replace('\u013a', 'l')  # LATIN SMALL LETTER L WITH ACUTE
    result = result.replace('\u013b', 'l')  # LATIN CAPITAL LETTER L WITH CEDILLA
    result = result.replace('\u013c', 'l')  # LATIN SMALL LETTER L WITH CEDILLA
    result = result.replace('\u013d', 'l')  # LATIN CAPITAL LETTER L WITH CARON
    result = result.replace('\u013e', 'l')  # LATIN SMALL LETTER L WITH CARON
    result = result.replace('\u013f', 'l')  # LATIN CAPITAL LETTER L WITH MIDDLE DOT
    result = result.replace('\u0140', 'l')  # LATIN SMALL LETTER L WITH MIDDLE DOT
    result = result.replace('\u0141', 'l')  # LATIN CAPITAL LETTER L WITH STROKE
    result = result.replace('\u0142', 'l')  # LATIN SMALL LETTER L WITH STROKE
    result = result.replace('\u0143', 'n')  # LATIN CAPITAL LETTER N WITH ACUTE
    result = result.replace('\u0144', 'n')  # LATIN SMALL LETTER N WITH ACUTE
    result = result.replace('\u0145', 'n')  # LATIN CAPITAL LETTER N WITH CEDILLA
    result = result.replace('\u0146', 'n')  # LATIN SMALL LETTER N WITH CEDILLA
    result = result.replace('\u0147', 'n')  # LATIN CAPITAL LETTER N WITH CARON
    result = result.replace('\u0148', 'n')  # LATIN SMALL LETTER N WITH CARON
    result = result.replace('\u0149', 'n')  # LATIN SMALL LETTER N PRECEDED BY APOSTROPHE
    result = result.replace('\u014a', 'n')  # LATIN CAPITAL LETTER ENG
    result = result.replace('\u014b', 'n')  # LATIN SMALL LETTER ENG
    result = result.replace('\u014c', 'o')  # LATIN CAPITAL LETTER O WITH MACRON
    result = result.replace('\u014d', 'o')  # LATIN SMALL LETTER O WITH MACRON
    result = result.replace('\u014e', 'o')  # LATIN CAPITAL LETTER O WITH BREVE
    result = result.replace('\u014f', 'o')  # LATIN SMALL LETTER O WITH BREVE
    result = result.replace('\u0150', 'o')  # LATIN CAPITAL LETTER O WITH DOUBLE ACUTE
    result = result.replace('\u0151', 'o')  # LATIN SMALL LETTER O WITH DOUBLE ACUTE
    result = result.replace('\u0152', 'oe')  # LATIN CAPITAL LIGATURE OE
    result = result.replace('\u0153', 'oe')  # LATIN SMALL LIGATURE OE
    result = result.replace('\u0154', 'r')  # LATIN CAPITAL LETTER R WITH ACUTE
    result = result.replace('\u0155', 'r')  # LATIN SMALL LETTER R WITH ACUTE
    result = result.replace('\u0156', 'r')  # LATIN CAPITAL LETTER R WITH CEDILLA
    result = result.replace('\u0157', 'r')  # LATIN SMALL LETTER R WITH CEDILLA
    result = result.replace('\u0158', 'r')  # LATIN CAPITAL LETTER R WITH CARON
    result = result.replace('\u0159', 'r')  # LATIN SMALL LETTER R WITH CARON
    result = result.replace('\u015a', 's')  # LATIN CAPITAL LETTER S WITH ACUTE
    result = result.replace('\u015b', 's')  # LATIN SMALL LETTER S WITH ACUTE
    result = result.replace('\u015c', 's')  # LATIN CAPITAL LETTER S WITH CIRCUMFLEX
    result = result.replace('\u015d', 's')  # LATIN SMALL LETTER S WITH CIRCUMFLEX
    result = result.replace('\u015e', 's')  # LATIN CAPITAL LETTER S WITH CEDILLA
    result = result.replace('\u015f', 's')  # LATIN SMALL LETTER S WITH CEDILLA
    result = result.replace('\u0160', 's')  # LATIN CAPITAL LETTER S WITH CARON
    result = result.replace('\u0161', 's')  # LATIN SMALL LETTER S WITH CARON
    result = result.replace('\u0162', 't')  # LATIN CAPITAL LETTER T WITH CEDILLA
    result = result.replace('\u0163', 't')  # LATIN SMALL LETTER T WITH CEDILLA
    result = result.replace('\u0164', 't')  # LATIN CAPITAL LETTER T WITH CARON
    result = result.replace('\u0165', 't')  # LATIN SMALL LETTER T WITH CARON
    result = result.replace('\u0166', 't')  # LATIN CAPITAL LETTER T WITH STROKE
    result = result.replace('\u0167', 't')  # LATIN SMALL LETTER T WITH STROKE
    result = result.replace('\u0168', 'u')  # LATIN CAPITAL LETTER U WITH TILDE
    result = result.replace('\u0169', 'u')  # LATIN SMALL LETTER U WITH TILDE
    result = result.replace('\u016a', 'u')  # LATIN CAPITAL LETTER U WITH MACRON
    result = result.replace('\u016b', 'u')  # LATIN SMALL LETTER U WITH MACRON
    result = result.replace('\u016c', 'u')  # LATIN CAPITAL LETTER U WITH BREVE
    result = result.replace('\u016d', 'u')  # LATIN SMALL LETTER U WITH BREVE
    result = result.replace('\u016e', 'u')  # LATIN CAPITAL LETTER U WITH RING ABOVE
    result = result.replace('\u016f', 'u')  # LATIN SMALL LETTER U WITH RING ABOVE
    result = result.replace('\u0170', 'u')  # LATIN CAPITAL LETTER U WITH DOUBLE ACUTE
    result = result.replace('\u0171', 'u')  # LATIN SMALL LETTER U WITH DOUBLE ACUTE
    result = result.replace('\u0172', 'u')  # LATIN CAPITAL LETTER U WITH OGONEK
    result = result.replace('\u0173', 'u')  # LATIN SMALL LETTER U WITH OGONEK
    result = result.replace('\u0174', 'w')  # LATIN CAPITAL LETTER W WITH CIRCUMFLEX
    result = result.replace('\u0175', 'w')  # LATIN SMALL LETTER W WITH CIRCUMFLEX
    result = result.replace('\u0176', 'y')  # LATIN CAPITAL LETTER Y WITH CIRCUMFLEX
    result = result.replace('\u0177', 'y')  # LATIN SMALL LETTER Y WITH CIRCUMFLEX
    result = result.replace('\u0178', 'y')  # LATIN CAPITAL LETTER Y WITH DIAERESIS
    result = result.replace('\u0179', 'z')  # LATIN CAPITAL LETTER Z WITH ACUTE
    result = result.replace('\u017a', 'z')  # LATIN SMALL LETTER Z WITH ACUTE
    result = result.replace('\u017b', 'z')  # LATIN CAPITAL LETTER Z WITH DOT ABOVE
    result = result.replace('\u017c', 'z')  # LATIN SMALL LETTER Z WITH DOT ABOVE
    result = result.replace('\u017d', 'z')  # LATIN CAPITAL LETTER Z WITH CARON
    result = result.replace('\u017e', 'z')  # LATIN SMALL LETTER Z WITH CARON
    result = result.replace('\u017f', 's')  # LATIN SMALL LETTER LONG S
    result = result.replace('\u0180', 'b')  # LATIN SMALL LETTER B WITH STROKE
    result = result.replace('\u0181', 'b')  # LATIN CAPITAL LETTER B WITH HOOK
    result = result.replace('\u0182', 'b')  # LATIN CAPITAL LETTER B WITH TOPBAR
    result = result.replace('\u0183', 'b')  # LATIN SMALL LETTER B WITH TOPBAR

    return result

# Rule 3 - Order of fields with identical leading elements
#
# does not apply


def filing_string_rule_3(input):
    result = input
    return result

# Rule 4 - Place names
#
# does not apply


def filing_string_rule_4(input):
    result = input
    return result

# Rule 5 - Identical filing entries
#
# Interpretted as meaning do them in some other respectible order,
# which I would use multiverse id for. However, since I am only
# concerned with base cards at this time, muid does not exist. So
# no-op.


def filing_string_rule_5(input):
    result = input
    return result

# Rule 6 - Abbreviations. File abbreviations exactly as written.
#
# No-op


def filing_string_rule_6(input):
    result = input
    return result

# Rule 7 - Treat bracketed data as signifcant
#
# No-op


def filing_string_rule_7(input):
    result = input
    return result

# Rule 8 - Hyphenated words.
#
# Treat words connected by a hyphen as separate words, regardless of
# language.


def filing_string_rule_8(input):
    result = input
    result = result.replace('-', ' ')  # dash
    result = result.replace('\u2013', ' ')  # endash
    result = result.replace('\u2014', ' ')  # emdash
    return result

# Rule 9 and 10 - Initial articles.
#
# Don't include them at the start of a title, unless it is a
# person or place. We will assume that all Cards are of a
# Person or Place (although this isn't quite true).
# $filingName =~ s/^a //gi;
# $filingName =~ s/^an //gi; # dash
# $filingName =~ s/^ye //gi; # dash
# $filingName =~ s/^de //gi; # dash
# $filingName =~ s/^d'//gi; # dash


def filing_string_rule_9(input):
    result = input
    return result


def filing_string_rule_10(input):
    result = input
    return result

# Rule 11 - Initials and acronyms
#
# Essentially, make periods and ellipses into spaces


_rule_11_m_0 = r'^\.(\d+)'
_rule_11_r_0 = r'0.\1'
_rule_11_m_1 = r' \.(\d+)'
_rule_11_r_1 = r' 0.\1'
_rule_11_m_2 = r'(\D+)\.(\D+)'
_rule_11_r_2 = r'\1 \2'
_rule_11_m_3 = r'(\D+)\.$'
_rule_11_r_3 = r'\1'
_rule_11_m_4 = r'^\.'
_rule_11_r_4 = r''


def filing_string_rule_11(input):
    result = input
    # Remember, Python's regexp only matches NON-OVERLAPPING occurances. So 'B.F.M. Big...' will not have all of the periods removed on the
    # first go.
    MAX_ITER = 20
    iter_count = 0
    running_sub_count = 1
    while running_sub_count > 0 and iter_count < MAX_ITER:
        iter_count = iter_count + 1
        # reset count...
        running_sub_count = 0
        result, num_of_subs = re.subn(_rule_11_m_0, _rule_11_r_0, result)
        running_sub_count = running_sub_count + num_of_subs
        result, num_of_subs = re.subn(_rule_11_m_1, _rule_11_r_1, result)
        running_sub_count = running_sub_count + num_of_subs
        result, num_of_subs = re.subn(_rule_11_m_2, _rule_11_r_2, result)
        running_sub_count = running_sub_count + num_of_subs
        result, num_of_subs = re.subn(_rule_11_m_3, _rule_11_r_3, result)
        running_sub_count = running_sub_count + num_of_subs
        result, num_of_subs = re.subn(_rule_11_m_4, _rule_11_r_4, result)
        running_sub_count = running_sub_count + num_of_subs
        #result, num_of_subs = re.subn(r'\u2026', r' ', result)
        #running_sub_count = running_sub_count + num_of_subs
    result = result.replace('\u2026', ' ')
    return result


# Rule 12 - Names with a prefix. Treat a prefix that is part of a
# name or place as a separate word unless it is joined to the rest
# of the name directly or by an apostrophe without a space. File
# letter by letter.
def filing_string_rule_12(input):
    result = input
    result = re.sub(r"([a-z])'([a-z])", r'\1\2', result)
    return result

# Rule 13
#
# Not taking action on roman numeral interpretation as arabic


def filing_string_rule_13(input):
    result = input
    return result


def numFix(num_match):
    result = num_match.group(1)
    result = result.replace(',', '')
    val = int(result)
    return '%09d' % val


def numFix2(num_match):
    result = num_match.group(2)
    result = result.replace(',', '')
    val = int(result)
    return num_match.group(1) + ('%09d' % val)

# Rule 14 - Numerals
#
# Complicated, since there could be unknown number of digits. Assuming 9 digits


def filing_string_rule_14(input):
    result = input

    # if it starts with a number, let's fix that number.
    result = re.sub(r'^([\d,]+)', numFix, result)

    # if there is a number in the middle, let's fix it
    result = re.sub(r'([^\\.0-9]+)([0-9,]+)', numFix2, result)

    return result


# Rule 15 -
#
# No-op
def filing_string_rule_15(input):
    result = input
    return result

# Rule 16  - Ignore all symbols except for "&"
#
# Putting this rule before Rule 14 since comma can be used in numbers and it is easier to process this first.


def filing_string_rule_16(input):
    result = input
    ignored_punctuation = [
        '!',
        '"',
        '#',
        '$',
        '%',
        "'",
        '(',
        ')',
        '*',
        '+',
        ',',
        '-',
        "\u2014",
        '/',
        ':',
        ';',
        '<',
        '=',
        '>',
        '?',
        '[',
        ']',
        '\\',
        '^',
        '_',
        '{',
        '|',
        '}',
        '~',
        "\u2022"]

    for u in '¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿':
        #ignored_punctuation.append(unicode(str(chr(u)), "ascii"))
        ignored_punctuation.append(u)

    lastone = ''
    for symb in ignored_punctuation:
        #result = re.sub(re.escape(symb), '', result)
        try:
            result = result.replace(symb, '')
        except UnicodeDecodeError as ude:
            sys.stderr.write("last one before error was {} {}\n".format(lastone, ord(lastone)))
            sys.stderr.write("this one ord is {}\n".format(ord(symb)))
            sys.stderr.write("values result:{} -- type is result:{}\n".format(result, type(result)))
            sys.stderr.write("symb:{} -- type is symb:{}\n".format(symb, type(symb)))
        lastone = symb
    return result

# This DOES NOT remove the period (".") on purpose!


def remove_punctuation(input):
    # Note that the Library of Congress system recognize the ampersand as a "word", not punctuation. So, let's rely on
    # filing rule 16, AND still remove the Ampersand.
    result = filing_string_rule_16(input)
    result = result.replace('&', ' ')
    # remove extra whitespace
    parts = result.split()
    result = " ".join(parts)
    return result
