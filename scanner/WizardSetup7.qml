import QtQuick 2.1
import QtQuick.Layouts 1.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

import UM 1.0 as UM
Rectangle 
{
    id:base
    width: 250
    height: 500
    color:"white"
    property int objectsMargin:10
    ColumnLayout
    {
        anchors.fill: parent;
        anchors.leftMargin:2
        Label
        {
            id:introText1
            text: "<b>Calibrating!</b>"
        }
        
        Image
        {
            id:placeholder1
            anchors.topMargin:objectsMargin
            source:"placeholder.png";
        }
        ProgressBar 
        {
            id: progressBar;

            minimumValue: 0;
            maximumValue: 100;

            Connections 
            {
                target: UM.Backend;
                onProcessingProgress: progressBar.value = amount;
            }
        }
        Label
        {
            id:warning_label
            text:switch(UM.ScannerEngineBackend.warningText)
            {
                case "Object":
                    return "Unable to locate calibration object";
                case "":
                    return "";
            }
        }
        NextButton
        {
            onClicked:
            {
                UM.ToolbarData.setState(8);
            }
            anchors.bottom: parent.bottom
            anchors.bottomMargin:10
        }
    }
}
