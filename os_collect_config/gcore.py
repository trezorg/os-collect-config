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
import logging

from oslo_config import cfg
from oslo_log import log

from os_collect_config import exc
from os_collect_config import merger

from os_collect_config.gcoreclient import GcoreHeatResourceClient

CONF = cfg.CONF
logger = log.getLogger(__name__)

opts = [
    cfg.StrOpt('access-token',
               help='Access token for API authentication'),
    cfg.StrOpt('refresh-token',
               help='Access token for API authentication'),
    cfg.IntOpt('project-id',
               help='ID of gcore project for API request'),
    cfg.StrOpt('api-url',
               help='URL for API requests'),
    cfg.StrOpt('stack-id',
               help='ID of the stack this deployment belongs to'),
    cfg.StrOpt('resource-name',
               help='Name of resource in the stack to be polled'),
    cfg.IntOpt('region-id',
               help='Gcore region id for API request'),
]

name = 'gcore'


def prepare_logging(level=logging.DEBUG):
    req_log = logging.getLogger('urllib3')
    req_log.setLevel(level=level)
    ch = logging.StreamHandler()
    ch.setLevel(level=level)
    req_log.addHandler(ch)
    if level == logging.DEBUG:
        try:
            from http.client import HTTPConnection
            HTTPConnection.debuglevel = 1
        except ImportError:
            pass


class Collector(object):

    def __init__(self, client=None, log_level=logging.DEBUG):
        self.client = client
        prepare_logging(level=log_level)

    def collect(self):
        if CONF.gcore.api_url is None:
            logger.info('No api_url configured.')
            raise exc.GcoreMetadataNotConfigured
        if CONF.gcore.access_token is None:
            logger.info('No access_token configured.')
            raise exc.GcoreMetadataNotConfigured
        if CONF.gcore.refresh_token is None:
            logger.info('No refresh_token configured.')
            raise exc.GcoreMetadataNotConfigured
        if CONF.gcore.project_id is None:
            logger.info('No project_id configured.')
            raise exc.GcoreMetadataNotConfigured
        if CONF.gcore.region_id is None:
            logger.info('No region_id configured.')
            raise exc.GcoreMetadataNotConfigured
        if CONF.gcore.stack_id is None:
            logger.info('No stack_id configured.')
            raise exc.GcoreMetadataNotConfigured
        if CONF.gcore.resource_name is None:
            logger.info('No resource_name configured.')
            raise exc.GcoreMetadataNotConfigured

        if self.client is None:
            self.client = GcoreHeatResourceClient.from_conf(CONF.gcore)

        try:
            logger.debug('Fetching metadata from %s', self.client.api_url)
            response = self.client.get_metadata()
            final_list = merger.merged_list_from_content(response, cfg.CONF.deployment_key, name)
            return final_list
        except Exception as e:
            logger.warn(str(e))
            raise exc.GcoreMetadataNotAvailable
