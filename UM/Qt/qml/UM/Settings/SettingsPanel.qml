import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Window 2.
import QtQuick.Controls.Styles 1.1

import UM 1.0 as UM

import ".."

Panel 
{
    id: settingsPanel
    color:"#ebebeb"
    title: "Settings";

    signal settingConfigurationRequested;
    signal saveClicked;

    contents: ColumnLayout
    {
        Layout.preferredWidth: 250
        Layout.preferredHeight: 500

        SettingsView {
            Layout.fillWidth: true
            Layout.fillHeight: true    
        }

        Button
        {
            Layout.fillWidth: true
            //text: "Save"
            onClicked: {
                settingsList.model.saveSettingValues()
                settingsPanel.saveClicked()
            }
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
                        width: childrenRect.width;
                        height: childrenRect.height;
                        spacing:4
                        Text
                        {
                            id:saveButtonText
                            text: "Save"
                            font.pointSize: 20
                            color:"#404040"
                        }
                        Image
                        {
                            id:saveButtonIcon

                            source: UM.Resources.getIcon("save_button.png")
                        }
                    }
                }
                background: Rectangle
                {
                    implicitWidth: 100
                    implicitHeight: 50
                    border.width: 1
                    border.color: "#404040"
                    gradient: Gradient
                    {
                        GradientStop
                        {
                            position: 0 ;
                            color: control.pressed ? "#B2B2B2" : "#A1A1A1"
                        }
                        GradientStop
                        {
                            position: 1 ;
                            color: control.pressed ? "#B2B2B2" : "#B2B2B2"
                        }
                    }
                }
            }
        }
    }
}
