import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
Rectangle 
{
    property alias contents: contentItem.children
    property alias buttons: buttonItem.children
    property int objectsMargin:5
    id:base
    width: 250
    height: 675
    color:"white"
    border.width:1
    MouseArea 
    {
        //Used to filter mouse events so they do not pass into the background.
        anchors.fill: parent;

        acceptedButtons: Qt.LeftButton | Qt.RightButton | Qt.MiddleButton
    }
    
    ColumnLayout
    {
        anchors.top:parent.top
        anchors.topMargin:objectsMargin
        anchors.left:parent.left
        anchors.leftMargin:objectsMargin
        width: base.width - objectsMargin * 2
        Layout.maximumHeight: base.height - objectsMargin * 2
        id:contentItem
    }
    
    ColumnLayout
    {
        id:buttonItem
        anchors.bottom:parent.bottom
        anchors.bottomMargin: base.objectsMargin 
        anchors.left:parent.left
        anchors.leftMargin: base.objectsMargin 
        Layout.fillWidth:true
    }
}