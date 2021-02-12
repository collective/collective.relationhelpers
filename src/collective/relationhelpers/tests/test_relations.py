from collective.relationhelpers.testing import COLLECTIVE_RELATIONHELPERS_INTEGRATION_TESTING
from collective.relationhelpers import api as relapi
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


class TestRelations(unittest.TestCase):

    layer = COLLECTIVE_RELATIONHELPERS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ('Manager',))

    def test_relation(self):
        doc1 = api.content.create(
            container=self.portal,
            type='Document',
            title='doc1',
            id='doc1',
            )
        doc2 = api.content.create(
            container=self.portal,
            type='Document',
            title='doc2',
            id='doc2',
            )
        relapi.link_objects(doc1, doc2, 'relatedItems')
        self.assertEqual(doc1.relatedItems[0].to_object, doc2)
        self.assertEqual(relapi.relations(doc1), [doc2])

    def test_broken_relation(self):
        doc1 = api.content.create(
            container=self.portal,
            type='Document',
            title='doc1',
            id='doc1',
            )
        doc2 = api.content.create(
            container=self.portal,
            type='Document',
            title='doc2',
            id='doc2',
            )
        relapi.link_objects(doc1, doc2, 'relatedItems')
        self.portal._delObject('doc2')
        self.assertEqual(relapi.relations(doc1), [])

    def test_relations_stats(self):
        doc1 = api.content.create(
            container=self.portal,
            type='Document',
            title='doc1',
            id='doc1',
            )
        doc2 = api.content.create(
            container=self.portal,
            type='Document',
            title='doc2',
            id='doc2',
            )
        relapi.link_objects(doc1, doc2, 'relatedItems')
        stats, broken = relapi.get_relations_stats()
        self.assertEqual(dict(stats), {'relatedItems': 1})
        self.assertEqual(dict(broken), {})
        view = api.content.get_view('inspect-relations', self.portal, self.request)
        self.assertTrue(view())
        self.assertTrue(view(relation='relatedItems'))


    def test_relations_stats_broken(self):
        doc1 = api.content.create(
            container=self.portal,
            type='Document',
            title='doc1',
            id='doc1',
            )
        doc2 = api.content.create(
            container=self.portal,
            type='Document',
            title='doc2',
            id='doc2',
            )
        doc3 = api.content.create(
            container=self.portal,
            type='Document',
            title='doc3',
            id='doc3',
            )
        relapi.link_objects(doc1, doc2, 'relatedItems')
        relapi.link_objects(doc1, doc3, 'relatedItems')
        self.portal._delObject('doc2')
        stats, broken = relapi.get_relations_stats()
        self.assertEqual(dict(stats), {'relatedItems': 1})
        self.assertEqual(dict(broken), {'relatedItems': 1})
        view = api.content.get_view('inspect-relations', self.portal, self.request)
        self.assertTrue(view())
        self.assertTrue(view(relation='relatedItems'))
