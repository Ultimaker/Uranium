import QtQuick 2.1
import QtQuick.Layouts 1.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

import UM 1.0 as UM
WizardPane
{
    contents: ColumnLayout
    {
        //anchors.fill: parent
        
        Text
        {
            id:introText
            text: "<b>Focus Beamer</b> <br> Move the focus slide of the projector so that the image is sharply projected on the calibration board. "
            Layout.maximumWidth:paneWidth
            
            wrapMode: Text.Wrap
        }
        
        Image
        {
            Layout.maximumWidth:paneWidth
            source:"placeholder.png";
            //anchors.horizontalCenter:parent.horizontalCenter
        }
        
        Text 
        {
            text: "When image is in foucs like the image above, you can continue to the next step."
            //Layout.maximumWidth:introText.Layout.maxiumWidth
            Layout.maximumWidth:paneWidth
            wrapMode: Text.Wrap
        }
    }
    buttons:NextButton
    {
        onClicked:
        {
            UM.ToolbarData.setState(5);
        }
    }
}
