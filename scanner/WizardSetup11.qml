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
            text: "<b>Export / share / print</b>"
        }
        
        Image
        {
            id:placeholder1
            anchors.topMargin:objectsMargin
            source:"placeholder.png";
        }
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
