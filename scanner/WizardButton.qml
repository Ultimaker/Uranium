import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

import UM 1.0 as UM

Button
{
    id:base
    property color backgroundColor: "black"
    property color foregroundColor: "white"
    property string text:""
    style: ButtonStyle 
    {
        background: Item 
        {
            implicitWidth: 240;
            implicitHeight:25;
            Rectangle 
            {
                id:background
                anchors.fill: parent;
                color: base.backgroundColor;
            }
        }
        label: Item 
        {
            Label 
            {
                id: text;
                text:base.text
                color:base.foregroundColor
                font.pointSize: UM.Theme.smallTextSize;
                font.bold:true
                anchors 
                {
                    left:parent.left
                    leftMargin:10
                    verticalCenter:parent.verticalCenter
                }
            }
        }
    }
}


