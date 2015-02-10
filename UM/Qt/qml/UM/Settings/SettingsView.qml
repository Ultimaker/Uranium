import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Window 2.
import QtQuick.Controls.Styles 1.1

import UM 1.0 as UM

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
                if(model.type == "enum") {
                    item.model = settingsList.model;
                }
                item.key = model.key
                item.index = parseInt(index);
            }

            Binding { target: item; property: "valid"; value: model.valid; }
            Binding { target: item; property: "value"; value: model.value; }

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

                label: Rectangle
                {
                    Layout.fillWidth: true
                    color: "transparent"
                    anchors.centerIn: parent
                    Row
                    {
                        anchors.centerIn: parent;
                        width: parent.width;
                        height: childrenRect.height;
                        spacing: 4
                        Image
                        {

                            source: UM.Resources.getIcon("icon_resolution.png")
                        }
                        Text
                        {
                            text: section
                            color:"#404040"
                        }

                    }
                }
                background: Rectangle
                {
                    implicitWidth: 100
                    implicitHeight: 50
                    color:"transparent"
                }
            }
            onClicked: settingsList.model.toggleCollapsedByCategory(section)
        }
    }
}
