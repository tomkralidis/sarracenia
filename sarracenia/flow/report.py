import sarracenia.moth
import copy
from sarracenia.flow import Flow
import logging

logger = logging.getLogger(__name__)

default_options = {'acceptUnmatched': True, 'nodupe_ttl': 0}


class Report(Flow):
    def __init__(self, options):

        super().__init__(options)
        self.plugins['load'].insert(0, 'sarracenia.flowcb.gather.message.Message')

        if hasattr(self.o, 'post_exchange'):
            self.plugins['load'].insert(0, 'sarracenia.flowcb.post.message.Message')
