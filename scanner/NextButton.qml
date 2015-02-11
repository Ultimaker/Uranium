import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

import UM 1.0 as UM

Button
{
    id:base
    property color backgroundColor: "black"
    property color foregroundColor: "white"
    style: ButtonStyle 
    {
        background: Item 
        {
            implicitWidth: 225;
            implicitHeight:25;
            Rectangle 
            {
                id:background
                anchors.fill: parent;
                color: base.backgroundColor;
            }
            Image
            {
                id:machineButtonIcon
                source: UM.Resources.getIcon("triangle.png")
                anchors.left:background.right
            }
            
        }
        label: Item 
        {
            Label 
            {
                id: text;
                text:"Next step"
                color:base.foregroundColor
                font.pointSize: UM.Theme.smallTextSize;
                font.bold:true
                anchors 
                {
                    left:parent.left
                    leftMargin:10
                    verticalCenter:parent.verticalCenter
                    //right: parent.right;
                }
            }
        }
    }
}


