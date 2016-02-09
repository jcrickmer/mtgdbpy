#!/bin/sh

./manage.py test cards.tests.helpertests && ./manage.py test cards.tests.tests && ./manage.py test cards.tests.loadertests && ./manage.py test cards.tests.searchtests && ./manage.py test cards.tests.nametests && ./manage.py test decks.tests.tests && ./manage.py test decks.tests.parsertests && ./manage.py test decks.tests.stattests
