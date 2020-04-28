# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

#Shoopdawoop

## \package UM
#  This is the main library for Uranium applications.

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")

import warnings
warnings.simplefilter("once", DeprecationWarning)
