import urllib.parse

import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry as Urllib3Retry
from requests.packages.urllib3.exceptions import ConnectTimeoutError

from django.conf import settings


class Retry(Urllib3Retry):

    def _is_connection_error(self, err):
        return isinstance(
            err,
            (
                # This is the default exception in the original implementation
                # of this method. It's a subclass of
                # urllib3.exceptions.HTTPError.
                ConnectTimeoutError,
                # PYDOTORG-STAGING-1N, PYDOTORG-STAGING-1P, PYDOTORG-STAGING-1P
                requests.ConnectionError,
            ),
        )


def purge_urls(*paths):
    """
    Purge Fastly cache for each given path.
    """
    api_key = getattr(settings, 'FASTLY_API_KEY', None)
    if not api_key or settings.DEBUG:
        return

    # TODO: We can extract this logic out in the future.
    session = requests.session()
    retry = Retry(
        total=3,
        backoff_factor=0.3,
        status_forcelist=(
            500,  # Internal Server Error
            502,  # Bad Gateway
            503,  # Service Unavailable
            504,  # Gateway Timeout
        ),
        # Default value for 'method_whitelist' doesn't include
        # PURGE since it's a non-standard verb.
        method_whitelist=(
            'PURGE',
        ),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    with session:
        session.headers['Fastly-Key'] = api_key
        for path in paths:
            url = urllib.parse.urljoin('https://www.python.org', path)
            # TODO: We should probably catch MaxRetryError and log it.
            session.request('PURGE', url)
