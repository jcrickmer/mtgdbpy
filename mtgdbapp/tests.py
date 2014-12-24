from django.test import TestCase, TransactionTestCase

from mtgdbapp.models import Color, Rarity, Type, Subtype, PhysicalCard, Card, BaseCard, CardRating
from django.db import IntegrityError
from django.core.exceptions import ValidationError

# Create your tests here.

class MigrationTestCase(TransactionTestCase):
	serialized_rollback = True
	#def test_basic_addition(self):
	#	serialized_rollback = True
	#	self.assertEqual(1 + 1, 2)

	def test_colors(self):
		serialized_rollback = True
		white = Color.objects.get(pk='W')
		blue = Color.objects.get(pk='U')
		black = Color.objects.get(pk='B')
		red = Color.objects.get(pk='R')
		green = Color.objects.get(pk='G')
		colorless = Color.objects.get(pk='c')
		colors = Color.objects.all()
		self.assertEqual(len(colors), 6)

	def test_rarities(self):
		serialized_rollback = True
		b = Rarity.objects.get(pk='b')
		self.assertEqual(b.sortorder, 0)
		c = Rarity.objects.get(pk='c')
		self.assertEqual(c.sortorder, 1)
		u = Rarity.objects.get(pk='u')
		self.assertEqual(u.sortorder, 2)
		r = Rarity.objects.get(pk='r')
		self.assertEqual(r.sortorder, 3)
		m = Rarity.objects.get(pk='m')
		self.assertEqual(m.sortorder, 4)
		s = Rarity.objects.get(pk='s')
		self.assertEqual(s.sortorder, 5)
		rarities = Rarity.objects.all()
		self.assertEqual(len(rarities), 6)


class TypeTestCase(TestCase):

	def test_type_create_basic(self):
		testType_s = 'Contraption'
		t = Type()
		t.type = testType_s
		t.save()

		t1 = Type.objects.filter(type__exact=testType_s).first()
		self.assertEqual(t1.type, testType_s)

	def test_type_uniqueness(self):
		testType_s = 'Contraption'
		t = Type()
		t.type = testType_s
		t.save()

		t2 = Type()
		t2.type = testType_s
		self.assertRaises(IntegrityError, t2.save)
		

class SubtypeTestCase(TestCase):

	def test_subtype_create_basic(self):
		testSubtype_s = 'Alien'
		st = Subtype()
		st.subtype = testSubtype_s
		st.save()

		st1 = Subtype.objects.filter(subtype__exact=testSubtype_s).first()
		self.assertEqual(st1.subtype, testSubtype_s)


	def test_subtype_uniqueness(self):		
		testSubtype_s = 'Alien'
		st = Subtype()
		st.subtype = testSubtype_s
		st.save()

		st2 = Subtype()
		st2.subtype = testSubtype_s
		self.assertRaises(IntegrityError, st2.save)

class PhysicalCardTestCase(TestCase):

	def test_physicalcard_create_basic(self):
		pc = PhysicalCard()
		self.assertIsNone(pc.id)
		pc.save()
		self.assertIsNotNone(pc.id)
		self.assertEquals(pc.layout, PhysicalCard.NORMAL)

		pc2 = PhysicalCard.objects.get(pk=pc.id)
		self.assertEqual(pc2.layout, pc.layout)

	def test_physicalcard_layout_choices(self):
		self.assertEquals(PhysicalCard.NORMAL, 'normal')
		self.assertEquals(PhysicalCard.SPLIT, 'split')
		self.assertEquals(PhysicalCard.FLIP, 'flip')
		self.assertEquals(PhysicalCard.DOUBLE, 'double-faced')
		self.assertEquals(PhysicalCard.TOKEN, 'token')
		self.assertEquals(PhysicalCard.PLANE, 'plane')
		self.assertEquals(PhysicalCard.SCHEME, 'scheme')
		self.assertEquals(PhysicalCard.PHENOMENON, 'phenomenon')
		self.assertEquals(PhysicalCard.LEVELER, 'leveler')
		self.assertEquals(PhysicalCard.VANGUARD, 'vanguard')

	def test_phsyicalcard_cardrating_none(self):
		pc = PhysicalCard()
		pc.save()

		self.assertRaises(CardRating.DoesNotExist, pc.getCardRating, None, None)
		self.assertRaises(CardRating.DoesNotExist, pc.getCardRating, 35432, 4652)

class BaseCardTestCase(TestCase):

	def test_basecard_create_basic(self):
		bc = BaseCard()
		self.assertIsNone(bc.id)
		self.assertRaises(IntegrityError, bc.save)

		pc = PhysicalCard()
		pc.save()
		bc = BaseCard()
		bc.physicalcard = pc

		# Still not good enough. We require a name
		self.assertRaisesRegexp(ValidationError, 'BaseCard must have a name', bc.clean)
		bc.name = 'Test Name'
		bc.clean()
		bc.save()
		self.assertIsNotNone(bc.id)
		self.assertEquals(bc.name, 'Test Name')
		self.assertEquals(bc.filing_name, 'test name')
		self.assertEquals(bc.rules_text,'')
		self.assertEquals(bc.mana_cost,'')
		self.assertEquals(bc.cmc, 0)
		self.assertIsNone(bc.power)
		self.assertIsNone(bc.toughness)
		self.assertIsNone(bc.loyalty)
		self.assertEquals(len(bc.get_rulings()), 0)
		# I REALLY DON'T LIKE THIS. REVISIT - Type is required. How do I enforce this requirement?
		self.assertEquals(len(bc.types.all()), 0)
		self.assertEquals(len(bc.subtypes.all()), 0)
		# I REALLY DON'T LIKE THIS. REVISIT - Color is required. How do I enforce this requirement?
		self.assertEquals(len(bc.colors.all()), 0)

		
class ViewsTestCase(TestCase):
	def test_basic_addition(self):
		self.assertEqual(1 + 1, 2)
