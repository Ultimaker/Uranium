// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1

import UM 1.1 as UM

PreferencesPage {
    id: base;

    title: qsTr("Machines");

    property variant currentMachine;

    function reset() {
    }
    resetEnabled: false;

    Row {
        id: buttons;

        width: childrenRect.width;
        height: childrenRect.height;

        Button { text: "Add..."; iconName: "list-add"; }
        Button { text: "Remove..."; iconName: "list-remove"; }
        Button { text: "Rename..."; iconName: "edit-rename"; }
    }

    Row {
        anchors {
            top: buttons.bottom;
            left: parent.left;
            right: parent.right;
            bottom: parent.bottom;
        }

        spacing: UM.Theme.sizes.default_margin.width;

        TableView {
            id: machines;

            anchors.top: parent.top;
            anchors.bottom: parent.bottom;

            width: parent.width / 2;

            TableViewColumn { role: "name" }

            headerVisible: false;

            model: UM.MachineInstancesModel { }

            onActivated: base.currentMachine = model.getItem(row);
        }

        Column {
            width: parent.width / 2;

            Label { text: base.currentMachine.name; font: UM.Theme.fonts.large; }
        }
    }
}
