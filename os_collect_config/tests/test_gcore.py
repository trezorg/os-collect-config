#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import fixtures
from oslo_config import cfg
import testtools
from testtools import matchers

from os_collect_config import collect
from os_collect_config import exc
from os_collect_config import gcore
from os_collect_config.gcoreclient import GcoreHeatResourceClient


META_DATA = {u'int1': 1,
             u'strfoo': u'foo',
             u'map_ab': {
                 u'a': 'apple',
                 u'b': 'banana',
             }}


class TestGcoreBase(testtools.TestCase):
    def setUp(self):
        super(TestGcoreBase, self).setUp()
        self.log = self.useFixture(fixtures.FakeLogger())
        self.useFixture(fixtures.NestedTempfile())
        collect.setup_conf()
        cfg.CONF.gcore.api_url = 'http://192.0.2.1:5000'
        cfg.CONF.gcore.access_token = '0123456789ABCDEF'
        cfg.CONF.gcore.refresh_token = 'FEDCBA9876543210'
        cfg.CONF.gcore.project_id = 1
        cfg.CONF.gcore.region_id = 1
        cfg.CONF.gcore.stack_id = 'a/c482680f-7238-403d-8f76-36acf0c8e0aa'
        cfg.CONF.gcore.resource_name = 'server'
        self.client = GcoreTestHeatResourceClient.from_conf(cfg.CONF.gcore)


class GcoreTestHeatResourceClient(GcoreHeatResourceClient):

    @classmethod
    def from_conf(cls, conf=None):
        if not conf:
            conf = cfg.CONF.gcore
        return super().from_conf(conf=conf)

    def get_metadata(self):
        return META_DATA


class TestGcore(TestGcoreBase):

    def test_collect_gcore(self):

        gcore_md = gcore.Collector(client=self.client).collect()
        self.assertThat(gcore_md, matchers.IsInstance(list))
        self.assertEqual('gcore', gcore_md[0][0])
        gcore_md = gcore_md[0][1]

        for k in ('int1', 'strfoo', 'map_ab'):
            self.assertIn(k, gcore_md)
            self.assertEqual(gcore_md[k], META_DATA[k])

        # level setting for urllib3.connectionpool.
        self.assertTrue(
            self.log.output == '' or
            self.log.output == 'Starting new HTTP connection (1): 192.0.2.1\n')

    def test_collect_gcore_no_api_url(self):
        cfg.CONF.gcore.api_url = None
        gcore_collect = gcore.Collector(client=self.client)
        self.assertRaises(exc.GcoreMetadataNotConfigured, gcore_collect.collect)
        self.assertIn('No api_url configured', self.log.output)

    def test_collect_gcore_no_access_token(self):
        cfg.CONF.gcore.access_token = None
        gcore_collect = gcore.Collector(client=self.client)
        self.assertRaises(exc.GcoreMetadataNotConfigured, gcore_collect.collect)
        self.assertIn('No access_token configured', self.log.output)

    def test_collect_gcore_no_refresh_token(self):
        cfg.CONF.gcore.refresh_token = None
        gcore_collect = gcore.Collector(client=self.client)
        self.assertRaises(exc.GcoreMetadataNotConfigured, gcore_collect.collect)
        self.assertIn('No refresh_token configured', self.log.output)

    def test_collect_gcore_no_project_id(self):
        cfg.CONF.gcore.project_id = None
        gcore_collect = gcore.Collector(client=self.client)
        self.assertRaises(exc.GcoreMetadataNotConfigured, gcore_collect.collect)
        self.assertIn('No project_id configured', self.log.output)

    def test_collect_gcore_no_region_id(self):
        cfg.CONF.gcore.region_id = None
        gcore_collect = gcore.Collector(client=self.client)
        self.assertRaises(exc.GcoreMetadataNotConfigured, gcore_collect.collect)
        self.assertIn('No region_id configured', self.log.output)

    def test_collect_gcore_no_stack_id(self):
        cfg.CONF.gcore.stack_id = None
        gcore_collect = gcore.Collector(client=self.client)
        self.assertRaises(exc.GcoreMetadataNotConfigured, gcore_collect.collect)
        self.assertIn('No stack_id configured', self.log.output)

    def test_collect_gcore_no_resource_name(self):
        cfg.CONF.gcore.resource_name = None
        gcore_collect = gcore.Collector(client=self.client)
        self.assertRaises(exc.GcoreMetadataNotConfigured, gcore_collect.collect)
        self.assertIn('No resource_name configured', self.log.output)
