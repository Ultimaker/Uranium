// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1
import QtQuick.Layouts 1.1

import UM 1.1 as UM

Button {
    id: base;

    property variant color;

    style: UM.Theme.styles.sidebar_category;

    signal configureSettingVisibility()
    signal showAllHidenInheritedSettings()

    signal showTooltip();
    signal hideTooltip();

    UM.SimpleButton {
        id: settingsButton

        visible: base.hovered || settingsButton.hovered
        height: base.height * 0.6
        width: base.height * 0.6

        anchors.verticalCenter: parent.verticalCenter
        anchors.right: parent.right
        anchors.rightMargin: UM.Theme.getSize("setting_preferences_button_margin").width

        color: hovered ? UM.Theme.getColor("setting_control_button_hover") : UM.Theme.getColor("setting_control_button");
        iconSource: UM.Theme.getIcon("settings");

        onClicked: {
            base.configureSettingVisibility()
        }
    }
    UM.SimpleButton
    {
        // This button shows when the setting has an inherited function, but is overriden by profile.
        id: inheritButton;

        anchors {
            right: settingsButton.left
            rightMargin: UM.Theme.getSize("default_margin").width / 2;
            verticalCenter: parent.verticalCenter;
        }

        visible: hiddenValuesCount > 0
        height: parent.height / 2;
        width: height;

        onClicked: {
            base.showAllHidenInheritedSettings()
        }

        color: UM.Theme.getColor("primary")
        iconSource: UM.Theme.getIcon("warning")

        MouseArea
        {
            id: inheritButtonMouseArea;

            anchors.fill: parent;

            acceptedButtons: Qt.NoButton
            hoverEnabled: true;

            onEntered: {
                base.showTooltip()
            }

            onExited: {
                base.hideTooltip();
            }
        }
    }
}

