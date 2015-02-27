import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

import UM 1.0 as UM

Button 
{
    id:base
    property string checkedImage
    property string uncheckedImage
    checkable:true
    style:ButtonStyle
    {
        background: Item
        {
            implicitWidth: control.width > 0 ? control.width : 16;
            implicitHeight: control.height > 0 ? control.height : 16;
            //Rectangle{anchors.fill:parent}
            //Component.onCompleted:{console.log(width); console.log(height);}
        }
        label: 
            Image
            {
                //width: control.width > 0 ? control.width : 16;
                //Height: control.height > 0 ? control.height : 16;
                id:displayImage
                source: control.checked ? checkedImage:uncheckedImage
            }
    }
}