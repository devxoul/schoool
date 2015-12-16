# -*- coding: utf-8 -*-

import sys

from redis import Redis

sys.modules[__name__] = Redis(db=1)
