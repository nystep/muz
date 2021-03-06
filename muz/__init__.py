
from __future__ import absolute_import

import os, logging

def configureLogger(log):
    logging.captureWarnings(True)
    log.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(muz.util.ColoredFormatter("%(levelname)18s %(name)s: %(message)s"))

    log.addHandler(ch)

log = logging.getLogger(__name__)

import muz.config
_config = muz.config.get(__name__, {
    "log": {
        "level": "warning",
    },
})

import muz.util
configureLogger(log)

from muz.main import initvfs, run, userdir, NAME, VERSION, init, bareInit
