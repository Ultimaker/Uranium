// Copyright (c) 2015 Ultimaker B.V.
// Uranium is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Dialogs 1.1

import UM 1.0 as UM

import "../Preferences"

PreferencesPage {
    //: Machine configuration page title.
    title: qsTr("Machine");

    contents: ColumnLayout {
        anchors.fill: parent;
        RowLayout {
            //: Active machine combo box label
            Label { text: qsTr("Active Machine:"); }
            ComboBox {
                id: machineCombo;
                Layout.fillWidth: true;
                model: UM.Models.machinesModel;
                textRole: "name";
                onCurrentIndexChanged: {
                    if(currentIndex != -1)
                        UM.Models.machinesModel.setActive(currentIndex);
                }

                Connections {
                    id: machineChange
                    target: UM.Application
                    onMachineChanged: machineCombo.currentIndex = machineCombo.find(UM.Application.machineName);
                }

                Component.onCompleted: machineCombo.currentIndex = machineCombo.find(UM.Application.machineName);
            }
            //: Remove active machine button
            Button { text: qsTr("Remove"); onClicked: confirmRemoveDialog.open(); }
        }
        ScrollView
        {
            Layout.fillWidth: true;
            Layout.fillHeight: true;

            ListView
            {
                delegate: settingDelegate
                model: UM.Models.settingsModel

                section.property: "category"
                section.delegate: Label { text: section }
            }
        }
    }

    Component
    {
        id: settingDelegate
        CheckBox
        {
            text: model.name;
            x: depth * 25
            checked: model.visibility
            onClicked: ListView.view.model.setVisibility(model.key, checked)
            enabled: !model.disabled
        }
    }

    MessageDialog {
        id: confirmRemoveDialog;

        icon: StandardIcon.Question;
        //: Remove machine confirmation dialog title
        title: qsTr("Confirm Machine Deletion");
        //: Remove machine confirmation dialog text
        text: qsTr("Are you sure you wish to remove the machine?");
        standardButtons: StandardButton.Yes | StandardButton.No;

        onYes: UM.Models.machinesModel.removeMachine(machineCombo.currentIndex);
    }
}
