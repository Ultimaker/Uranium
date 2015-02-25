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
            text: "<b>Object Characteristics</b><br>Choose an object setting that best matches the object that you're about to scan.."
            wrapMode: Text.Wrap
            Layout.maximumWidth:parent.width
        }
        
        Image
        {
            Layout.maximumWidth:parent.width
            source:"placeholder.png";
        }
        
        ExclusiveGroup { id: objectType }
        ColumnLayout
        {
            id: objectTypeSelection
            RadioButton 
            {
                text: "Simple / smooth"
                checked: true
                exclusiveGroup: objectType
            }
            RadioButton 
            {
                text: "Detailed"
                exclusiveGroup: objectType
            }
            RadioButton 
            {
                text: "Dificult object"
                exclusiveGroup: objectType
            }
        }
    }
    buttons:NextButton
    {
        onClicked:
        {
            UM.ToolbarData.setState(9);
        }
    }

}
