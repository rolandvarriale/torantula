import random
import logging

from urlparse import urlparse
from scrapy.exceptions import IgnoreRequest

from scrapy.utils.project import get_project_settings
settings = get_project_settings()
"""
These middlewares are specified in settings, and called by the spider for each
outgoing request generated between the engine and the downloader.
"""


class RandomUserAgentMiddleware(object):
    """
    Intercepts each outbound request and randomizes the user agent.
    Also logs each outbound request.
    """

    def process_request(self, request, spider):
        """
        This function is automatically called by the spider for each request.
        :param request: Webpage request generated by the spider
        :param spider: The spider currently crawling (passed the request)
        :return: None
        """

        ua = random.choice(settings.get('USER_AGENT_LIST'))
        request.headers.setdefault('User-Agent', ua)
        logging.info("%s:\n" % request)


class ProxyMiddleware(object):
    """
    Appends proxy access information to each outbound request.
    """

    def process_request(self, request, spider):
        """
        This function is automatically called by the spider for each request
        :param request: Webpage request generated by the spider
        :param spider: The spider currently crawling (passed the request)
        :return: None
        """

        if spider.tor_activated:
            request.meta['proxy'] = settings.get('HTTP_PROXY')
        request.errback = spider.handle_timeout


class IgnoreDomainMiddleware(object):
    """
    Raises an IgnoreRequest if the outbound request is towards a domain
    that should be ignored.
    """

    def process_request(self, request, spider):
        """
        This function is automatically called by the spider for each request
        :param request: Webpage request generated by the spider
        :param spider: The spider currently crawling (passed the request)
        :return: Raises an IgnoreRequest or returns None
        """

        req_domain = urlparse(request.url).netloc
        if spider.dcount.ignore_this(req_domain):
            raise IgnoreRequest("IGNORING REQUEST TO: %s" % req_domain)

    def process_response(self, request, response, spider):
        res_domain = urlparse(response.url).netloc
        spider.dcount.update_domain(res_domain)
        return response
