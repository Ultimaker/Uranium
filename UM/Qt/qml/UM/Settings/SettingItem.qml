// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Layouts 1.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

import UM 1.0 as UM

Rectangle {
    id: base;

    property string name;
    property string description;
    property variant value;
    property string unit;
    property int valid;
    property string type;
    property int depth;

    property variant options;
    property int index;
    property variant key;

    property bool overridden;

    signal contextMenuRequested();
    signal itemValueChanged(variant value);
    signal showTooltip(variant position);
    signal hideTooltip();
    signal resetRequested();

    property bool hovered: false;

    MouseArea 
    {
        id: mouse;

        anchors.fill: parent;

        acceptedButtons: Qt.RightButton;
        hoverEnabled: true;

        onClicked: base.contextMenuRequested();

        onEntered: {
            hoverTimer.start();
            base.hovered = true;
        }

        onExited: {
            if(controlContainer.item && controlContainer.item.hovered) {
                return;
            }

            base.hovered = false;
            hoverTimer.stop();
            base.hideTooltip();
        }

        Timer {
            id: hoverTimer;
            interval: 500;
            repeat: false;

            onTriggered: base.showTooltip({ x: mouse.mouseX, y: mouse.mouseY });
        }
    }
    property variant style: SettingItemStyle { }

    Label
    {
        id: label;

        anchors.left: parent.left;
        anchors.leftMargin: UM.Theme.sizes.section_icon_column.width + 5
        anchors.right: controlContainer.left;
        anchors.rightMargin: base.style.spacing;
        anchors.verticalCenter: parent.verticalCenter

        height: UM.Theme.sizes.section.height;
        verticalAlignment: Text.AlignVCenter;

        text: base.name
        elide: Text.ElideMiddle;

        color: base.style.controlTextColor;
        font: base.style.labelFont;
    }

    Loader {
        id: controlContainer;

        anchors.right: parent.right;
        anchors.verticalCenter: parent.verticalCenter

        width: base.style.controlWidth;
        height: base.style.fixedHeight > 0 ? base.style.fixedHeight : parent.height;

        property variant itemStyle: base.style

        source:
        {
            switch(base.type)
            {
                case "int":
                    return "SettingTextField.qml"
                case "float":
                    return "SettingTextField.qml"
                case "double":
                    return "SettingTextField.qml"
                case "enum":
                    return "SettingComboBox.qml"
                case "boolean":
                    return "SettingCheckBox.qml"
                default:
                    return "SettingUnknown.qml"
            }
        }

        Connections {
            target: controlContainer.item;
            onValueChanged: {
                base.itemValueChanged(value);
            }
            onHoveredChanged: {
                if(controlContainer.item.hovered) {
                    hoverTimer.start();
                } else {
                    if(!mouse.containsMouse) {
                        hoverTimer.stop();
                        base.hideTooltip();
                    }
                }
            }
        }
    }

    Button {
        anchors {
            right: parent.right;
            verticalCenter: parent.verticalCenter;
        }
        visible: base.overridden;
        tooltip: "Reset to Default";

        text: "R";

        height: parent.height;
        width: height;

        onClicked: base.resetRequested()

        style: ButtonStyle {
            background: Rectangle {
                border.width: base.style.controlBorderWidth;
                border.color: base.style.controlBorderColor;
                color: control.hovered ? base.style.controlHighlightColor : base.style.controlColor;
            }
        }
    }
}
