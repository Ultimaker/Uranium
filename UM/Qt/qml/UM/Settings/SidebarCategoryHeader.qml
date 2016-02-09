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

    Button{
        id: settingsButton
        visible: base.hovered || settingsButton.hovered
        height: base.height * 0.6
        width: base.height * 0.6
        anchors.verticalCenter: parent.verticalCenter
        anchors.right: parent.right
        anchors.rightMargin: UM.Theme.sizes.setting_preferences_button_margin.width
        style: ButtonStyle {
            background: UM.RecolorImage {
                id: settingsImage
                width: control.width
                height: control.height
                sourceSize.width: width
                sourceSize.height: width
                color: control.hovered ? UM.Theme.colors.setting_control_button_hover : UM.Theme.colors.setting_control_button
                source: UM.Theme.icons.settings
            }
            label: Label{}
        }
        onClicked: {
            preferences.visible = true;
            preferences.setPage(2);
            preferences.getCurrentItem().scrollToSection(model.id);
        }
    }
}

