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
            text: "<b>Edit object</b> <br> Stitch the clouds."
        }
        
        Image
        {
            id:placeholder1
            source:"placeholder.png";
        }
        Label
        {
           
            text: "Make sure you select two layers at a time."
        }
        Label
        {
            text:"<b>Suface Finish</b>"
        }
        
        Rectangle 
        {
            id:spacer
            width: 246
            color:"black"
            height: 2
        }
        
        CheckBox
        {
            text:"Smooth"
        }
        
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
