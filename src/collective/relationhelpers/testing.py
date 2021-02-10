# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import PloneSandboxLayer

import collective.relationhelpers


class CollectiveRelationhelpersLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=collective.relationhelpers)

    def setUpPloneSite(self, portal):
        portal.acl_users.userFolderAddUser(
            SITE_OWNER_NAME, SITE_OWNER_PASSWORD, ['Manager'], []
        )


COLLECTIVE_RELATIONHELPERS_FIXTURE = CollectiveRelationhelpersLayer()


COLLECTIVE_RELATIONHELPERS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_RELATIONHELPERS_FIXTURE,),
    name='CollectiveRelationhelpersLayer:IntegrationTesting',
)


COLLECTIVE_RELATIONHELPERS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_RELATIONHELPERS_FIXTURE,),
    name='CollectiveRelationhelpersLayer:FunctionalTesting',
)
