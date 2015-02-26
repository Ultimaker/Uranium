import QtQuick 2.1
import QtQuick.Layouts 1.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

import UM 1.0 as UM
WizardPane
{
    contents: ColumnLayout
    {
        anchors.fill: parent
        Text
        {
            text: "<b>Calibrating!</b>"
            wrapMode: Text.Wrap
            Layout.maximumWidth:parent.width
        }
        
        Image
        {
            Layout.maximumWidth:parent.width
            source:"placeholder.png";
        }
        ProgressBar 
        {
            id: progressBar;

            minimumValue: 0;
            maximumValue: 100;
            Layout.maximumWidth:parent.width
            Connections 
            {
                target: UM.Backend;
                onProcessingProgress: progressBar.value = amount;
            }
        }
        Text
        {
            id:status_label
            text:switch(UM.ScannerEngineBackend.statusText)
            {
                case "Object":
                    return "Unable to locate calibration object";
                case "":
                    return "";
                case "Processing":
                    return "Processing data";
                case "Capturing":
                    return "Capturing data";
            }
            wrapMode: Text.Wrap
            Layout.preferredWidth:parent.width
            Layout.maximumWidth:parent.width
        }
    }
    buttons: NextButton
    {
        onClicked:
        {
            UM.ToolbarData.setState(8);
        }
    }
}
