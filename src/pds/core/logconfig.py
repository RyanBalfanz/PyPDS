#!/usr/bin/env python
# encoding: utf-8
"""
logconfig.py

Created by Ryan Matthew Balfanz on 2009-08-05.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

import logging
import sys

# Set the message format
format = logging.Formatter("%(levelname)-10s %(asctime)s %(message)s")

# Create a CRITICAL message handler
crit_hand = logging.StreamHandler(sys.stderr)
crit_hand.setLevel(logging.CRITICAL)
crit_hand.setFormatter(format)

# Create a handler for routing to a file
applog_hand = logging.FileHandler('app.log')
applog_hand.setFormatter(format)

# Create a top-level logger called 'app'
app_log = logging.getLogger("app")
app_log.setLevel(logging.INFO)
app_log.addHandler(applog_hand)


