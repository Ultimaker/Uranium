import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

import "."

ButtonStyle {
    id: base;
    property bool down: control.pressed || (control.checkable && control.checked);

    property color backgroundColor: Theme.toolbarButtonBackgroundColor;
    property color foregroundColor: Theme.toolbarButtonForegroundColor;

    property color backgroundHighlightColor: Theme.toolbarButtonBackgroundHighlightColor;
    property color foregroundHighlightColor: Theme.toolbarButtonForegroundHighlightColor;

    property color backgroundDisabledColor: Theme.toolbarButtonBackgroundDisabledColor;
    property color foregroundDisabledColor: Theme.toolbarButtonForegroundDisabledColor;

    background: Item {
        implicitWidth: control.width > 0 ? control.width : Theme.toolbarButtonWidth;
        implicitHeight: control.height > 0 ? control.height : Theme.toolbarButtonHeight;

        Rectangle {
            id: backgroundItem;

            anchors.fill: parent;
            anchors.bottomMargin: Theme.toolbarBorderSize;
            color: base.backgroundColor;
        }

        Rectangle {
            anchors.horizontalCenter: parent.left;
            anchors.top: parent.top;
            anchors.bottom: parent.bottom;
            width: 1;
            color: Theme.borderColor;
        }

        Rectangle {
            anchors.horizontalCenter: parent.right;
            anchors.top: parent.top;
            anchors.bottom: parent.bottom;
            width: 1;
            color: Theme.borderColor;
        }

        states: [
            State {
                name: 'down';
                when: base.down;

                PropertyChanges { target: backgroundItem; color: base.backgroundHighlightColor; }
            }
        ]

        transitions: [
            Transition {
                ColorAnimation { duration: 100; }
            }
        ]
    }
    label: Item {
        anchors.fill: parent;
        property bool down: control.pressed || (control.checkable && control.checked);
        RecolorImage {
            id: icon;

            anchors.top: parent.top;
            anchors.topMargin: 2;
            anchors.horizontalCenter: parent.horizontalCenter;
            width: Theme.toolbarIconWidth;
            height: Theme.toolbarIconHeight;
            source: control.iconSource

            color: base.foregroundColor;
        }
        Label {
            id: text;
            anchors {
                bottom: parent.bottom;
                bottomMargin: 2;
                left: parent.left;
                right: parent.right;
            }
            text: control.text;
            color: base.foregroundColor;

            font.capitalization: Font.AllUppercase;
            font.pointSize: Theme.tinyTextSize;
            horizontalAlignment: Text.AlignHCenter;
            wrapMode: Text.Wrap;
        }

        states: [
            State {
                name: 'down';
                when: base.down;

                PropertyChanges { target: icon; color: base.foregroundHighlightColor; }
                PropertyChanges { target: text; color: base.foregroundHighlightColor; }
            },
            State {
                name: 'disabled';
                when: !control.enabled;

                PropertyChanges { target: icon; color: base.foregroundDisabledColor; }
                PropertyChanges { target: text; color: base.foregroundDisabledColor; }
            }
        ]

        transitions: [
            Transition {
                ColorAnimation { duration: 100; }
            }
        ]
    }
}
