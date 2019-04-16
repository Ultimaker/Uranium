# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

#Shoopdawoop

## \package UM
#  This is the main library for Uranium applications.


#Temporary translation entries.
#We add these translated strings so that they enter into our translation templates.
#These translated strings are for features that may yet be merged into 3.3.
from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("uranium")
_ = i18n_catalog.i18nc("@info:status", "Your configuration seems to be corrupt. Something seems to be wrong with the following profiles:\n- {profiles}\nWould you like to reset to factory defaults?")
_ = i18n_catalog.i18nc("@info:status", "Your configuration seems to be corrupt.")
_ = i18n_catalog.i18nc("@info:title", "Configuration errors")
_ = i18n_catalog.i18nc("@info:button", "Reset your configuration to factory defaults.")

import warnings
warnings.simplefilter("once", DeprecationWarning)
