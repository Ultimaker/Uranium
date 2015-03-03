import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Window 2.
import QtQuick.Controls.Styles 1.1

import UM 1.0 as UM
import ".."

ScrollView
{
    id: base;

    property alias listHeight: settingsList.contentHeight;

    signal showDescription(string text, real x, real y);

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
                    case "double":
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
                acceptedButtons: Qt.LeftButton | Qt.RightButton;
                onClicked: {
                    if(mouse.button == Qt.LeftButton)
                    {
                        var position = mapToItem(null, 0, height / 2);
                        base.showDescription(model.description, position.x, position.y);
                    }
                    else
                    {
                        contextMenu.popup();
                    }
                }
            }

            Menu
            {
                id: contextMenu;

                MenuItem {
                    //: Settings context menu action
                    text: qsTr("Hide this setting");
                    onTriggered: settingsList.model.setVisibility(model.key, false);
                }
                MenuItem {
                    //: Settings context menu action
                    text: qsTr("Configure setting visiblity...");
                    onTriggered: settingsPanel.settingConfigurationRequested();
                }
            }
        }

        section.delegate: Button
        {
            id:categoryButton
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
            Behavior on height {NumberAnimation{}}
            Behavior on opacity {NumberAnimation{}}
            height: settingsList.model.checkVisibilityCategory(section) ? 40:0;
            opacity: settingsList.model.checkVisibilityCategory(section) ? 1:0;
            
            
            onClicked: 
            { 
                settingsList.model.toggleCollapsedByCategory(section);
            }
            Connections 
            {
                target: settingsList.model;
                onDataChanged: {
                    categoryButton.opacity = settingsList.model.checkVisibilityCategory(section) ? 1:0;
                    categoryButton.height = settingsList.model.checkVisibilityCategory(section) ? 40:0;
                }
            }
        }
    }
}
