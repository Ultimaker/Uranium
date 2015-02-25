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
            id:introText
            text: "<b>Hardware setup</b><br>Choose a hardware setup. We recommend choosing 'basic setup' if this is your first time using Argus."
            wrapMode: Text.Wrap
            Layout.maximumWidth:parent.width
        }
        Rectangle 
        {
            id:spacers
            width:parent.width
            color:"black"
            height: 2
        }
        Image
        {
            id:scanImage
            Layout.maximumWidth:parent.width
            source:"placeholder.png";
        }
        
        ExclusiveGroup { id: setupType }
        ColumnLayout
        {
            id: setupSelection

            RadioButton 
            {
                text: "Basic setup"
                checked: true
                exclusiveGroup: setupType
            }
            RadioButton 
            {
                text: "Same as last time"
                exclusiveGroup: setupType
            }
            RadioButton 
            {
                text: "Custom / free setup"
                exclusiveGroup: setupType
            }
        }
        Rectangle 
        {
            width: parent.width
            color:"black"
            height: 2
        }
    }
    buttons:NextButton
    {
        onClicked:
        {
            UM.ToolbarData.setState(2);
        }
    }
}
