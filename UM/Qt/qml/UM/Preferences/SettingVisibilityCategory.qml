// Copyright (c) 2022 Ultimaker B.V.
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 2.1

import UM 1.5 as UM

import ".."

UM.CategoryButton
{
    id: base

    // To avoid overlapping with the scrollBars
    anchors.rightMargin: 2 * UM.Theme.getSize("thin_margin").width

    categoryIcon: definition ? UM.Theme.getIcon(definition.icon) : ""
    labelText: definition ? definition.label : ""
    expanded: definition ? definition.expanded : false

    signal showTooltip(string text)
    signal hideTooltip()
    signal contextMenuRequested()

    onClicked: expanded ? settingDefinitionsModel.collapseRecursive(definition.key) : settingDefinitionsModel.expandRecursive(definition.key)
}
