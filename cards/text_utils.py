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
        result = '_'
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
    result = re.sub(r'\u00c0', 'a', result)  # LATIN CAPITAL LETTER A WITH GRAVE
    result = re.sub(r'\u00c1', 'a', result)  # LATIN CAPITAL LETTER A WITH ACUTE
    result = re.sub(r'\u00c2', 'a', result)  # LATIN CAPITAL LETTER A WITH CIRCUMFLEX
    result = re.sub(r'\u00c3', 'a', result)  # LATIN CAPITAL LETTER A WITH TILDE
    result = re.sub(r'\u00c4', 'a', result)  # LATIN CAPITAL LETTER A WITH DIAERESIS
    result = re.sub(r'\u00c5', 'a', result)  # LATIN CAPITAL LETTER A WITH RING ABOVE
    result = re.sub(r'\u00c6', 'ae', result)  # LATIN CAPITAL LETTER AE
    result = re.sub(r'\u00c7', 'c', result)  # LATIN CAPITAL LETTER C WITH CEDILLA
    result = re.sub(r'\u00c8', 'e', result)  # LATIN CAPITAL LETTER E WITH GRAVE
    result = re.sub(r'\u00c9', 'e', result)  # LATIN CAPITAL LETTER E WITH ACUTE
    result = re.sub(r'\u00ca', 'e', result)  # LATIN CAPITAL LETTER E WITH CIRCUMFLEX
    result = re.sub(r'\u00cb', 'e', result)  # LATIN CAPITAL LETTER E WITH DIAERESIS
    result = re.sub(r'\u00cc', 'i', result)  # LATIN CAPITAL LETTER I WITH GRAVE
    result = re.sub(r'\u00cd', 'i', result)  # LATIN CAPITAL LETTER I WITH ACUTE
    result = re.sub(r'\u00ce', 'i', result)  # LATIN CAPITAL LETTER I WITH CIRCUMFLEX
    result = re.sub(r'\u00cf', 'i', result)  # LATIN CAPITAL LETTER I WITH DIAERESIS
    result = re.sub(r'\u00d0', 'd', result)  # LATIN CAPITAL LETTER ETH
    result = re.sub(r'\u00d1', 'n', result)  # LATIN CAPITAL LETTER N WITH TILDE
    result = re.sub(r'\u00d2', 'o', result)  # LATIN CAPITAL LETTER O WITH GRAVE
    result = re.sub(r'\u00d3', 'o', result)  # LATIN CAPITAL LETTER O WITH ACUTE
    result = re.sub(r'\u00d4', 'o', result)  # LATIN CAPITAL LETTER O WITH CIRCUMFLEX
    result = re.sub(r'\u00d5', 'o', result)  # LATIN CAPITAL LETTER O WITH TILDE
    result = re.sub(r'\u00d6', 'o', result)  # LATIN CAPITAL LETTER O WITH DIAERESIS
    result = re.sub(r'\u00d7', ' ', result)  # MULTIPLICATION SIGN
    result = re.sub(r'\u00d8', 'o', result)  # LATIN CAPITAL LETTER O WITH STROKE
    result = re.sub(r'\u00d9', 'u', result)  # LATIN CAPITAL LETTER U WITH GRAVE
    result = re.sub(r'\u00da', 'u', result)  # LATIN CAPITAL LETTER U WITH ACUTE
    result = re.sub(r'\u00db', 'u', result)  # LATIN CAPITAL LETTER U WITH CIRCUMFLEX
    result = re.sub(r'\u00dc', 'u', result)  # LATIN CAPITAL LETTER U WITH DIAERESIS
    result = re.sub(r'\u00dd', 'y', result)  # LATIN CAPITAL LETTER Y WITH ACUTE
    result = re.sub(r'\u00de', 'th', result)  # LATIN CAPITAL LETTER THORN
    result = re.sub(r'\u00df', 's', result)  # LATIN SMALL LETTER SHARP S
    result = re.sub(r'\u00e0', 'a', result)  # LATIN SMALL LETTER A WITH GRAVE
    result = re.sub(r'\u00e1', 'a', result)  # LATIN SMALL LETTER A WITH ACUTE
    result = re.sub(r'\u00e2', 'a', result)  # LATIN SMALL LETTER A WITH CIRCUMFLEX
    result = re.sub(r'\u00e3', 'a', result)  # LATIN SMALL LETTER A WITH TILDE
    result = re.sub(r'\u00e4', 'a', result)  # LATIN SMALL LETTER A WITH DIAERESIS
    result = re.sub(r'\u00e5', 'a', result)  # LATIN SMALL LETTER A WITH RING ABOVE
    result = re.sub(r'\u00e6', 'ae', result)  # LATIN SMALL LETTER AE
    result = re.sub(r'\u00e7', 'c', result)  # LATIN SMALL LETTER C WITH CEDILLA
    result = re.sub(r'\u00e8', 'e', result)  # LATIN SMALL LETTER E WITH GRAVE
    result = re.sub(r'\u00e9', 'e', result)  # LATIN SMALL LETTER E WITH ACUTE
    result = re.sub(r'\u00ea', 'e', result)  # LATIN SMALL LETTER E WITH CIRCUMFLEX
    result = re.sub(r'\u00eb', 'e', result)  # LATIN SMALL LETTER E WITH DIAERESIS
    result = re.sub(r'\u00ec', 'i', result)  # LATIN SMALL LETTER I WITH GRAVE
    result = re.sub(r'\u00ed', 'i', result)  # LATIN SMALL LETTER I WITH ACUTE
    result = re.sub(r'\u00ee', 'i', result)  # LATIN SMALL LETTER I WITH CIRCUMFLEX
    result = re.sub(r'\u00ef', 'i', result)  # LATIN SMALL LETTER I WITH DIAERESIS
    result = re.sub(r'\u00f0', 'd', result)  # LATIN SMALL LETTER ETH
    result = re.sub(r'\u00f1', 'n', result)  # LATIN SMALL LETTER N WITH TILDE
    result = re.sub(r'\u00f2', 'o', result)  # LATIN SMALL LETTER O WITH GRAVE
    result = re.sub(r'\u00f3', 'o', result)  # LATIN SMALL LETTER O WITH ACUTE
    result = re.sub(r'\u00f4', 'o', result)  # LATIN SMALL LETTER O WITH CIRCUMFLEX
    result = re.sub(r'\u00f5', 'o', result)  # LATIN SMALL LETTER O WITH TILDE
    result = re.sub(r'\u00f6', 'o', result)  # LATIN SMALL LETTER O WITH DIAERESIS
    result = re.sub(r'\u00f7', ' ', result)  # DIVISION SIGN
    result = re.sub(r'\u00f8', 'o', result)  # LATIN SMALL LETTER O WITH STROKE
    result = re.sub(r'\u00f9', 'u', result)  # LATIN SMALL LETTER U WITH GRAVE
    result = re.sub(r'\u00fa', 'u', result)  # LATIN SMALL LETTER U WITH ACUTE
    result = re.sub(r'\u00fb', 'u', result)  # LATIN SMALL LETTER U WITH CIRCUMFLEX
    result = re.sub(r'\u00fc', 'u', result)  # LATIN SMALL LETTER U WITH DIAERESIS
    result = re.sub(r'\u00fd', 'y', result)  # LATIN SMALL LETTER Y WITH ACUTE
    result = re.sub(r'\u00fe', 'th', result)  # LATIN SMALL LETTER THORN
    result = re.sub(r'\u00ff', 'y', result)  # LATIN SMALL LETTER Y WITH DIAERESIS
    result = re.sub(r'\u0100', 'a', result)  # LATIN CAPITAL LETTER A WITH MACRON
    result = re.sub(r'\u0101', 'a', result)  # LATIN SMALL LETTER A WITH MACRON
    result = re.sub(r'\u0102', 'a', result)  # LATIN CAPITAL LETTER A WITH BREVE
    result = re.sub(r'\u0103', 'a', result)  # LATIN SMALL LETTER A WITH BREVE
    result = re.sub(r'\u0104', 'a', result)  # LATIN CAPITAL LETTER A WITH OGONEK
    result = re.sub(r'\u0105', 'a', result)  # LATIN SMALL LETTER A WITH OGONEK
    result = re.sub(r'\u0106', 'c', result)  # LATIN CAPITAL LETTER C WITH ACUTE
    result = re.sub(r'\u0107', 'c', result)  # LATIN SMALL LETTER C WITH ACUTE
    result = re.sub(r'\u0108', 'c', result)  # LATIN CAPITAL LETTER C WITH CIRCUMFLEX
    result = re.sub(r'\u0109', 'c', result)  # LATIN SMALL LETTER C WITH CIRCUMFLEX
    result = re.sub(r'\u010a', 'c', result)  # LATIN CAPITAL LETTER C WITH DOT ABOVE
    result = re.sub(r'\u010b', 'c', result)  # LATIN SMALL LETTER C WITH DOT ABOVE
    result = re.sub(r'\u010c', 'c', result)  # LATIN CAPITAL LETTER C WITH CARON
    result = re.sub(r'\u010d', 'c', result)  # LATIN SMALL LETTER C WITH CARON
    result = re.sub(r'\u010e', 'd', result)  # LATIN CAPITAL LETTER D WITH CARON
    result = re.sub(r'\u010f', 'd', result)  # LATIN SMALL LETTER D WITH CARON
    result = re.sub(r'\u0110', 'd', result)  # LATIN CAPITAL LETTER D WITH STROKE
    result = re.sub(r'\u0111', 'd', result)  # LATIN SMALL LETTER D WITH STROKE
    result = re.sub(r'\u0112', 'e', result)  # LATIN CAPITAL LETTER E WITH MACRON
    result = re.sub(r'\u0113', 'e', result)  # LATIN SMALL LETTER E WITH MACRON
    result = re.sub(r'\u0114', 'e', result)  # LATIN CAPITAL LETTER E WITH BREVE
    result = re.sub(r'\u0115', 'e', result)  # LATIN SMALL LETTER E WITH BREVE
    result = re.sub(r'\u0116', 'e', result)  # LATIN CAPITAL LETTER E WITH DOT ABOVE
    result = re.sub(r'\u0117', 'e', result)  # LATIN SMALL LETTER E WITH DOT ABOVE
    result = re.sub(r'\u0118', 'e', result)  # LATIN CAPITAL LETTER E WITH OGONEK
    result = re.sub(r'\u0119', 'e', result)  # LATIN SMALL LETTER E WITH OGONEK
    result = re.sub(r'\u011a', 'e', result)  # LATIN CAPITAL LETTER E WITH CARON
    result = re.sub(r'\u011b', 'e', result)  # LATIN SMALL LETTER E WITH CARON
    result = re.sub(r'\u011c', 'g', result)  # LATIN CAPITAL LETTER G WITH CIRCUMFLEX
    result = re.sub(r'\u011d', 'g', result)  # LATIN SMALL LETTER G WITH CIRCUMFLEX
    result = re.sub(r'\u011e', 'g', result)  # LATIN CAPITAL LETTER G WITH BREVE
    result = re.sub(r'\u011f', 'g', result)  # LATIN SMALL LETTER G WITH BREVE
    result = re.sub(r'\u0120', 'g', result)  # LATIN CAPITAL LETTER G WITH DOT ABOVE
    result = re.sub(r'\u0121', 'g', result)  # LATIN SMALL LETTER G WITH DOT ABOVE
    result = re.sub(r'\u0122', 'g', result)  # LATIN CAPITAL LETTER G WITH CEDILLA
    result = re.sub(r'\u0123', 'g', result)  # LATIN SMALL LETTER G WITH CEDILLA
    result = re.sub(r'\u0124', 'h', result)  # LATIN CAPITAL LETTER H WITH CIRCUMFLEX
    result = re.sub(r'\u0125', 'h', result)  # LATIN SMALL LETTER H WITH CIRCUMFLEX
    result = re.sub(r'\u0126', 'h', result)  # LATIN CAPITAL LETTER H WITH STROKE
    result = re.sub(r'\u0127', 'h', result)  # LATIN SMALL LETTER H WITH STROKE
    result = re.sub(r'\u0128', 'i', result)  # LATIN CAPITAL LETTER I WITH TILDE
    result = re.sub(r'\u0129', 'i', result)  # LATIN SMALL LETTER I WITH TILDE
    result = re.sub(r'\u012a', 'i', result)  # LATIN CAPITAL LETTER I WITH MACRON
    result = re.sub(r'\u012b', 'i', result)  # LATIN SMALL LETTER I WITH MACRON
    result = re.sub(r'\u012c', 'i', result)  # LATIN CAPITAL LETTER I WITH BREVE
    result = re.sub(r'\u012d', 'i', result)  # LATIN SMALL LETTER I WITH BREVE
    result = re.sub(r'\u012e', 'i', result)  # LATIN CAPITAL LETTER I WITH OGONEK
    result = re.sub(r'\u012f', 'i', result)  # LATIN SMALL LETTER I WITH OGONEK
    result = re.sub(r'\u0130', 'i', result)  # LATIN CAPITAL LETTER I WITH DOT ABOVE
    result = re.sub(r'\u0131', 'i', result)  # LATIN SMALL LETTER DOTLESS I
    result = re.sub(r'\u0132', 'ij', result)  # LATIN CAPITAL LIGATURE IJ
    result = re.sub(r'\u0133', 'ij', result)  # LATIN SMALL LIGATURE IJ
    result = re.sub(r'\u0134', 'j', result)  # LATIN CAPITAL LETTER J WITH CIRCUMFLEX
    result = re.sub(r'\u0135', 'j', result)  # LATIN SMALL LETTER J WITH CIRCUMFLEX
    result = re.sub(r'\u0136', 'k', result)  # LATIN CAPITAL LETTER K WITH CEDILLA
    result = re.sub(r'\u0137', 'k', result)  # LATIN SMALL LETTER K WITH CEDILLA
    result = re.sub(r'\u0138', 'kr', result)  # LATIN SMALL LETTER KRA
    result = re.sub(r'\u0139', 'l', result)  # LATIN CAPITAL LETTER L WITH ACUTE
    result = re.sub(r'\u013a', 'l', result)  # LATIN SMALL LETTER L WITH ACUTE
    result = re.sub(r'\u013b', 'l', result)  # LATIN CAPITAL LETTER L WITH CEDILLA
    result = re.sub(r'\u013c', 'l', result)  # LATIN SMALL LETTER L WITH CEDILLA
    result = re.sub(r'\u013d', 'l', result)  # LATIN CAPITAL LETTER L WITH CARON
    result = re.sub(r'\u013e', 'l', result)  # LATIN SMALL LETTER L WITH CARON
    result = re.sub(r'\u013f', 'l', result)  # LATIN CAPITAL LETTER L WITH MIDDLE DOT
    result = re.sub(r'\u0140', 'l', result)  # LATIN SMALL LETTER L WITH MIDDLE DOT
    result = re.sub(r'\u0141', 'l', result)  # LATIN CAPITAL LETTER L WITH STROKE
    result = re.sub(r'\u0142', 'l', result)  # LATIN SMALL LETTER L WITH STROKE
    result = re.sub(r'\u0143', 'n', result)  # LATIN CAPITAL LETTER N WITH ACUTE
    result = re.sub(r'\u0144', 'n', result)  # LATIN SMALL LETTER N WITH ACUTE
    result = re.sub(r'\u0145', 'n', result)  # LATIN CAPITAL LETTER N WITH CEDILLA
    result = re.sub(r'\u0146', 'n', result)  # LATIN SMALL LETTER N WITH CEDILLA
    result = re.sub(r'\u0147', 'n', result)  # LATIN CAPITAL LETTER N WITH CARON
    result = re.sub(r'\u0148', 'n', result)  # LATIN SMALL LETTER N WITH CARON
    result = re.sub(r'\u0149', 'n', result)  # LATIN SMALL LETTER N PRECEDED BY APOSTROPHE
    result = re.sub(r'\u014a', 'n', result)  # LATIN CAPITAL LETTER ENG
    result = re.sub(r'\u014b', 'n', result)  # LATIN SMALL LETTER ENG
    result = re.sub(r'\u014c', 'o', result)  # LATIN CAPITAL LETTER O WITH MACRON
    result = re.sub(r'\u014d', 'o', result)  # LATIN SMALL LETTER O WITH MACRON
    result = re.sub(r'\u014e', 'o', result)  # LATIN CAPITAL LETTER O WITH BREVE
    result = re.sub(r'\u014f', 'o', result)  # LATIN SMALL LETTER O WITH BREVE
    result = re.sub(r'\u0150', 'o', result)  # LATIN CAPITAL LETTER O WITH DOUBLE ACUTE
    result = re.sub(r'\u0151', 'o', result)  # LATIN SMALL LETTER O WITH DOUBLE ACUTE
    result = re.sub(r'\u0152', 'oe', result)  # LATIN CAPITAL LIGATURE OE
    result = re.sub(r'\u0153', 'oe', result)  # LATIN SMALL LIGATURE OE
    result = re.sub(r'\u0154', 'r', result)  # LATIN CAPITAL LETTER R WITH ACUTE
    result = re.sub(r'\u0155', 'r', result)  # LATIN SMALL LETTER R WITH ACUTE
    result = re.sub(r'\u0156', 'r', result)  # LATIN CAPITAL LETTER R WITH CEDILLA
    result = re.sub(r'\u0157', 'r', result)  # LATIN SMALL LETTER R WITH CEDILLA
    result = re.sub(r'\u0158', 'r', result)  # LATIN CAPITAL LETTER R WITH CARON
    result = re.sub(r'\u0159', 'r', result)  # LATIN SMALL LETTER R WITH CARON
    result = re.sub(r'\u015a', 's', result)  # LATIN CAPITAL LETTER S WITH ACUTE
    result = re.sub(r'\u015b', 's', result)  # LATIN SMALL LETTER S WITH ACUTE
    result = re.sub(r'\u015c', 's', result)  # LATIN CAPITAL LETTER S WITH CIRCUMFLEX
    result = re.sub(r'\u015d', 's', result)  # LATIN SMALL LETTER S WITH CIRCUMFLEX
    result = re.sub(r'\u015e', 's', result)  # LATIN CAPITAL LETTER S WITH CEDILLA
    result = re.sub(r'\u015f', 's', result)  # LATIN SMALL LETTER S WITH CEDILLA
    result = re.sub(r'\u0160', 's', result)  # LATIN CAPITAL LETTER S WITH CARON
    result = re.sub(r'\u0161', 's', result)  # LATIN SMALL LETTER S WITH CARON
    result = re.sub(r'\u0162', 't', result)  # LATIN CAPITAL LETTER T WITH CEDILLA
    result = re.sub(r'\u0163', 't', result)  # LATIN SMALL LETTER T WITH CEDILLA
    result = re.sub(r'\u0164', 't', result)  # LATIN CAPITAL LETTER T WITH CARON
    result = re.sub(r'\u0165', 't', result)  # LATIN SMALL LETTER T WITH CARON
    result = re.sub(r'\u0166', 't', result)  # LATIN CAPITAL LETTER T WITH STROKE
    result = re.sub(r'\u0167', 't', result)  # LATIN SMALL LETTER T WITH STROKE
    result = re.sub(r'\u0168', 'u', result)  # LATIN CAPITAL LETTER U WITH TILDE
    result = re.sub(r'\u0169', 'u', result)  # LATIN SMALL LETTER U WITH TILDE
    result = re.sub(r'\u016a', 'u', result)  # LATIN CAPITAL LETTER U WITH MACRON
    result = re.sub(r'\u016b', 'u', result)  # LATIN SMALL LETTER U WITH MACRON
    result = re.sub(r'\u016c', 'u', result)  # LATIN CAPITAL LETTER U WITH BREVE
    result = re.sub(r'\u016d', 'u', result)  # LATIN SMALL LETTER U WITH BREVE
    result = re.sub(r'\u016e', 'u', result)  # LATIN CAPITAL LETTER U WITH RING ABOVE
    result = re.sub(r'\u016f', 'u', result)  # LATIN SMALL LETTER U WITH RING ABOVE
    result = re.sub(r'\u0170', 'u', result)  # LATIN CAPITAL LETTER U WITH DOUBLE ACUTE
    result = re.sub(r'\u0171', 'u', result)  # LATIN SMALL LETTER U WITH DOUBLE ACUTE
    result = re.sub(r'\u0172', 'u', result)  # LATIN CAPITAL LETTER U WITH OGONEK
    result = re.sub(r'\u0173', 'u', result)  # LATIN SMALL LETTER U WITH OGONEK
    result = re.sub(r'\u0174', 'w', result)  # LATIN CAPITAL LETTER W WITH CIRCUMFLEX
    result = re.sub(r'\u0175', 'w', result)  # LATIN SMALL LETTER W WITH CIRCUMFLEX
    result = re.sub(r'\u0176', 'y', result)  # LATIN CAPITAL LETTER Y WITH CIRCUMFLEX
    result = re.sub(r'\u0177', 'y', result)  # LATIN SMALL LETTER Y WITH CIRCUMFLEX
    result = re.sub(r'\u0178', 'y', result)  # LATIN CAPITAL LETTER Y WITH DIAERESIS
    result = re.sub(r'\u0179', 'z', result)  # LATIN CAPITAL LETTER Z WITH ACUTE
    result = re.sub(r'\u017a', 'z', result)  # LATIN SMALL LETTER Z WITH ACUTE
    result = re.sub(r'\u017b', 'z', result)  # LATIN CAPITAL LETTER Z WITH DOT ABOVE
    result = re.sub(r'\u017c', 'z', result)  # LATIN SMALL LETTER Z WITH DOT ABOVE
    result = re.sub(r'\u017d', 'z', result)  # LATIN CAPITAL LETTER Z WITH CARON
    result = re.sub(r'\u017e', 'z', result)  # LATIN SMALL LETTER Z WITH CARON
    result = re.sub(r'\u017f', 's', result)  # LATIN SMALL LETTER LONG S
    result = re.sub(r'\u0180', 'b', result)  # LATIN SMALL LETTER B WITH STROKE
    result = re.sub(r'\u0181', 'b', result)  # LATIN CAPITAL LETTER B WITH HOOK
    result = re.sub(r'\u0182', 'b', result)  # LATIN CAPITAL LETTER B WITH TOPBAR
    result = re.sub(r'\u0183', 'b', result)  # LATIN SMALL LETTER B WITH TOPBAR

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

# Rule 7 - Trreat bracketed data as signifcant
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
    result = re.sub(r'-', ' ', result)  # dash
    result = re.sub(r'\u2013', ' ', result)  # endash
    result = re.sub(r'\u2014', ' ', result)  # emdash
    return result

# Rule 9 and 10 - Initial articles.
#
# Don't include them at the start of a title, unless it is a
# person or place. We will assume that all Cards are of a
# Person or Place (although this isn't quite true).
#$filingName =~ s/^a //gi;
#$filingName =~ s/^an //gi; # dash
#$filingName =~ s/^ye //gi; # dash
#$filingName =~ s/^de //gi; # dash
#$filingName =~ s/^d'//gi; # dash


def filing_string_rule_9(input):
    result = input
    return result


def filing_string_rule_10(input):
    result = input
    return result

# Rule 11 - Initials and acronyms
#
# Essentially, make periods and ellipses into spaces


def filing_string_rule_11(input):
    result = input
    result = re.sub(r'^\.(\d+)', r'0.\1', result)
    result = re.sub(r' \.(\d+)', r' 0.\1', result)
    result = re.sub(r'(\D+)\.(\D+)', r'\1 \2', result)
    result = re.sub(r'(\D+)\.$', r'\1', result)
    result = re.sub(r'^\.', r'', result)
    result = re.sub(r'\u2026', r' ', result)
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
    result = re.sub(r',', '', result)
    val = int(result)
    return '%09d' % val


def numFix2(num_match):
    result = num_match.group(2)
    result = re.sub(r',', '', result)
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
        '~']
    for u in range(161, 191):
        ignored_punctuation.append(chr(u))

    for symb in ignored_punctuation:
        result = re.sub(re.escape(symb), '', result)

    return result
