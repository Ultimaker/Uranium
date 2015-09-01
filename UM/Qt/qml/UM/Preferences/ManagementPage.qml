// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1

import UM 1.1 as UM

PreferencesPage {
    id: base;

    property alias model: objectList.model;
    property string nameRole: "name";
    property bool detailsVisible: true;

    property variant currentItem: null;

    default property alias details: detailsPane.children;

    signal itemActivated();
    signal addObject();
    signal removeObject();
    signal renameObject();

    property alias addEnabled: addButton.enabled;
    property alias removeEnabled: removeButton.enabled;
    property alias renameEnabled: renameButton.enabled;

    property alias buttons: buttons.children;

    property alias addText: addButton.text;

    resetEnabled: false;

    Row {
        id: buttons;

        width: childrenRect.width;
        height: childrenRect.height;

        Button {
            id: addButton;
            text: catalog.i18nc("@action:button", "Add");
            iconName: "list-add";
            onClicked: base.addObject();
        }
        Button {
            id: removeButton;
            text: catalog.i18nc("@action:button", "Remove");
            iconName: "list-remove";
            onClicked: base.removeObject();
        }
        Button {
            id: renameButton;
            text: "Rename";
            iconName: "edit-rename";
            onClicked: base.renameObject();
        }
    }

    Item {
        anchors {
            top: buttons.bottom;
            left: parent.left;
            right: parent.right;
            bottom: parent.bottom;
        }

        TableView {
            id: objectList;

            anchors {
                top: parent.top;
                bottom: parent.bottom;
                left: parent.left;
            }

            width: base.detailsVisible ? parent.width / 2 : parent.width;

            TableViewColumn { role: base.nameRole; }

            headerVisible: false;

            onActivated: {
                base.currentItem = model.getItem(row);
                base.itemActivated();
            }

            Component.onCompleted: {
                if(model.count > 0) {
                    selection.select(0, 0);
                    base.currentItem = model.getItem(0);
                }
            }
        }

        Item {
            id: detailsPane;

            anchors {
                left: objectList.right;
                leftMargin: UM.Theme.sizes.default_margin.width;
                top: parent.top;
                bottom: parent.bottom;
                right: parent.right;
            }

            visible: base.detailsVisible;
        }

        UM.I18nCatalog { id: catalog; name: "uranium"; }
    }
}
