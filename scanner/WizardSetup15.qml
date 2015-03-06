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
            text: "<b>Export / share / print</b>"
            wrapMode: Text.Wrap
            Layout.maximumWidth:parent.width
        }
        
        Image
        {
            source:"placeholder.png";
            Layout.maximumWidth:parent.width
        }
    }    
    buttons: ColumnLayout
    {    
        WizardButton
        {
            text:"Export to file"
        }
        WizardButton
        {
            text:"Share on youmagine"
        }
        WizardButton
        {
            text:"Send to cura"
        }
    }
}
