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
import requests

from oslo_config import cfg
from oslo_log import log

CONF = cfg.CONF
logger = log.getLogger(__name__)


def check_unauthenticated_response(response):
    if response.status_code == 401:
        return True
    return False


class GcoreBaseClient(object):

    FIELDS = ('api_url', 'region_id', 'project_id', 'access_token', 'refresh_token')

    HEADERS = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }

    def __init__(self, api_url, region_id, project_id, access_token, refresh_token):
        self.api_url = api_url
        self.region_id = region_id
        self.project_id = project_id
        self.access_token = access_token
        self.refresh_token = refresh_token

    @property
    def session(self):
        return requests.Session()

    @property
    def refresh_url(self):
        return f'{self.api_url}/v1/token/refresh'

    @classmethod
    def from_conf(cls, conf):
        return cls(**{field: getattr(conf, field) for field in cls.FIELDS})

    @property
    def auth_headers(self):
        return {
            'Authorization': f'Bearer: {self.access_token}',
            'Accept': 'application/json',
        }

    def postprocess_refresh(self):
        pass

    def process_refresh_token(self):
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        body = {'token': self.refresh_token}
        response = self.session.post(
            self.refresh_token, headers=headers, json=body
        )
        response.raise_for_status()
        tokens = response.json()
        self.access_token = tokens['access_token']
        self.refresh_token = tokens['refresh_token']
        self.postprocess_refresh()

    def request(self, func, *args, **kwargs):
        response = func(*args, **kwargs)
        if check_unauthenticated_response(response):
            self.refresh_token()
            response = func(*args, **kwargs)
        response.raise_for_status()
        return response


class GcoreHeatResourceClient(GcoreBaseClient):

    FIELDS = GcoreBaseClient.FIELDS + ('stack_id', 'resource_name')

    def __init__(self, api_url, region_id, project_id,
                 stack_id, resource_name, access_token, refresh_token):
        super().__init__(
            api_url=api_url,
            region_id=region_id,
            project_id=project_id,
            access_token=access_token,
            refresh_token=refresh_token
        )
        self.stack_id = stack_id
        self.resource_name = resource_name

    @property
    def metadata_url(self):
        return (
            f'{self.api_url}/v1/{self.project_id}/{self.region_id}/heat/{self.stack_id}/'
            f'resources/{self.resource_name}/metadata'
        )

    def _get_metadata(self):
        response = self.session.get(self.metadata_url, headers=self.auth_headers)
        response.raise_for_status()
        return response

    def get_metadata(self):
        return self.request(self._get_metadata).json()
