// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.2
import QtQuick.Controls.Styles 1.2
import QtQuick.Window 2.2

import UM 1.1 as UM

Item {
    id: base;

    width: 0;
    height: 0;

    property variant position: mapToItem(null, 0, 0)

    property int currentIndex;

    Item {
        id: settingsPanel;

        width: childrenRect.width;
        height: childrenRect.height;

        opacity: 0;
        Behavior on opacity { NumberAnimation { } }

        Rectangle {
            id: arrow;
            width: 35;
            height: 35;
            rotation: 45;
            anchors.verticalCenter: parent.verticalCenter;
        }

        Rectangle {
            width: childrenRect.width;
            height: childrenRect.height;

            anchors.left: arrow.horizontalCenter;

            DropArea {
                anchors.fill: parent;
            }

            Column {
                spacing: UM.Theme.sizes.default_margin.width;

                UM.SettingItem {
                    width: UM.Theme.sizes.setting.width;
                    height: UM.Theme.sizes.setting.height;

                    name: "Profile"
                    type: "enum"

                    style: UM.Theme.styles.setting_item;

                    options: UM.ProfilesModel { selectGlobal: true }
                }

                Repeater {
                    model: overriddenSettingsModel;

                    UM.SettingItem {
                        width: UM.Theme.sizes.setting.width;
                        height: UM.Theme.sizes.setting.height;

                        name: model.name;
                        type: model.type;
                        value: model.value;

                        style: UM.Theme.styles.setting_item;

                        Button {
                            anchors.right: parent.right;
                            text: "x";
                        }
                    }
                }

                Button {
                    text: "+ Override Setting";

                    style: ButtonStyle {
                        background: Item { }
                        label: Label {
                            text: control.text;
                            color: control.hovered ? "blue" : "black"
                        }
                    }
                }

                Button {
                    text: "Close";
                    onClicked: {
                        settingsPanel.opacity = 0;
                    }
                }
            }
        }
    }

    Repeater {
        model: UM.ActiveTool.properties.Model;
        delegate: Button {
            x: ((model.x + 1.0) / 2.0) * UM.Application.mainWindow.width - base.position.x - width / 2
            y: -((model.y + 1.0) / 2.0) * UM.Application.mainWindow.height + (UM.Application.mainWindow.height - base.position.y) + height / 2

            width: 35;
            height: 35;

            text: "+";
            onClicked: {
                base.currentIndex = index;

                if(x < UM.Application.mainWindow.width / 2) {
                    settingsPanel.anchors.left = right;
                } else {
                    settingsPanel.anchors.right = left;
                }
                settingsPanel.anchors.verticalCenter = verticalCenter;

                settingsPanel.opacity = 1;
            }

            style: ButtonStyle {
                background: Rectangle {
                    width: control.width;
                    height: control.height;
                    radius: control.height / 2;

                    color: "white";

                    border.color: "black";
                    border.width: 1;
                }
            }
        }
    }

    ListModel {
        id: overriddenSettingsModel

        ListElement { name: "Layer Height"; type: "float"; value: "0.1"; }
    }
}
