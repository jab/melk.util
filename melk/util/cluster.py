# Copyright (C) 2009 The Open Planning Project
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301
# USA

import logging 
import threading
from threading import Thread 
from melk.selection.lsh import lsh
import traceback 

log = logging.getLogger(__name__)


class UserClusterJob(object):
    """
    Performs locality-sensitive hashing with the given hashfamily, k, and L
    parameters to cluster users based on similar starred items.
    """
    def __init__(self, model, hashfamily, k, L):
        self.model = model
        self.hashfamily = hashfamily
        self.k = k
        self.L = L
        self.seeds = hashfamily.seeds(k, L)

    def __call__(self):
        log.info('user clustering...')
        try:
            for user in self.model.all_users():
                if not user.has_role('member'):
                    continue
                log.debug('processing users/%s' % user.uri)
                user.clear_clusters()
                starred = [item.uri for item in user.starred.iter_latest()]
                for cluster in lsh(starred, self.hashfamily, self.k, self.L, self.seeds):
                    user.add_cluster(cluster)
                user.put()
        finally:
            log.info('finished user clustering')
            self.model.session_complete()
