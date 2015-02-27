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
        Label
        {
            id:introText1
            text: "<b>Scan object</b> <br> You're now scanning."
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
            text:switch(prog.visible ? UM.ScannerEngineBackend.statusText : "")
            {
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
    buttons:Item
    {
        Layout.fillWidth:true
        Layout.preferredHeight: 25;
        
        NextButton
        {
            id:nextButton
            onClicked:
            {
                UM.ToolbarData.setState(11);
            }
            visible:false
        }

        ProgressBar 
        {
            id: prog;

            minimumValue: 0;
            maximumValue: 100;
            Layout.maximumWidth:parent.width
            Layout.preferredWidth:200
            Layout.preferredHeight:25
            Layout.minimumWidth:200
            Layout.minimumHeight:25
            width: 200
            height: 25
            
            Connections 
            {
                target: UM.Backend;
                onProcessingProgress: 
                {
                    nextButton.visible = amount != 100 ? false : true;
                    prog.visible = amount != 100 ? true : false;
                    prog.value = amount;
                }
            }
        }
    }
}
