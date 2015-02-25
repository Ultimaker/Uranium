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
            text: "<b>Edit object</b> <br> Stitch the clouds."
            wrapMode: Text.Wrap
            Layout.maximumWidth:parent.width
        }
        
        Image
        {
            Layout.maximumWidth:parent.width
            source:"placeholder.png";
        }
        Text
        {
           
            text: "Make sure you select two layers at a time."
            wrapMode: Text.Wrap
            Layout.maximumWidth:parent.width
        }
        Text
        {
            text:"<b>Suface Finish</b>"
            wrapMode: Text.Wrap
            Layout.maximumWidth:parent.width
        }
        
        Rectangle 
        {
            width:parent.width
            color:"black"
            height: 2
        }
        CheckBox
        {
            text:"Smooth"
        }
    }
    buttons:ColumnLayout
    {    

        WizardButton
        {
            text:"Scan Extra"
        }
        WizardButton
        {
            text:"Merge to solid"
        }
    }
}
