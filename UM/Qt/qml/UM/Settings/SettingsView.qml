import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Window 2.
import QtQuick.Controls.Styles 1.1

import UM 1.0 as UM
import ".."

ScrollView
{
    property alias listHeight: settingsList.contentHeight;

    ListView
    {
        id:settingsList

        model: UM.Models.settingsModel
        clip: true
        section.property: "category"

        delegate: Loader
        {
            opacity: (model.visibility && !model.collapsed) ? 1 : 0
            Behavior on opacity { NumberAnimation { } }
            height: (model.visibility && !model.collapsed) ? 30 : 0
            Behavior on height { NumberAnimation { } }

            width: ListView.view.width;

            source:
            {
                switch(model.type)
                {
                    case "int":
                        return "SettingTextField.qml"
                    case "float":
                        return "SettingTextField.qml"
                    case "enum":
                        return "SettingComboBox.qml"
                    case "boolean":
                        return "SettingCheckBox.qml"
                }
            }

            onLoaded:
            {
                item.model = ListView.view.model;
                if(model.type == "enum") {
                    item.options = model.options;
                }
                item.key = model.key
                item.index = parseInt(index);
            }

            Binding { target: item; property: "name"; value: model.name; }
            Binding { target: item; property: "valid"; value: model.valid; }
            Binding { target: item; property: "value"; value: model.value; }
            Binding { target: item; property: "unit"; value: model.unit; }

            MouseArea
            {
                anchors.fill: parent;
                acceptedButtons: Qt.RightButton;
                onClicked: contextMenu.popup();
            }

            Menu
            {
                id: contextMenu;

                MenuItem { text: "Hide this setting"; onTriggered: settingsList.model.setVisibility(model.key, false); }
                MenuItem { text: "Configure setting visiblity..."; onTriggered: settingsPanel.settingConfigurationRequested(); }
            }

        }

        section.delegate: Button
        {
            style: ButtonStyle
            {

                label: Item
                {
                    Row
                    {
                        anchors.fill: parent;
                        spacing: Theme.defaultMargin;
                        Image
                        {

                            source: UM.Resources.getIcon("icon_resolution.png")
                        }
                        Label
                        {
                            text: section
                            color:"#404040"
                        }

                    }
                }
                background: Item
                {
                    implicitWidth: control.width;
                    implicitHeight: control.height;
                }
            }
            width: settingsList.width;
            height: 40;
            text: section;
            onClicked: settingsList.model.toggleCollapsedByCategory(section)
        }
    }
}
