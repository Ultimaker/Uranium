// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1
import QtQuick.Layouts 1.1

import UM 1.0 as UM

Button {
    id: base;

    Layout.preferredHeight: UM.Theme.sizes.section.height;
    Layout.preferredWidth: UM.Theme.sizes.sidebar.width;

    property variant color;
    style: UM.Theme.styles.sidebar_category;
}
