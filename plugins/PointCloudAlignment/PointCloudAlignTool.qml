import QtQuick 2.2
import QtQuick.Controls 1.2

import UM 1.0 as UM

Item 
{
    width:250
    height:250
    Button 
    {
        text: "Stitch clouds" 
        id: stitch_button
        anchors.bottom: parent.bottom
        enabled: UM.ActiveTool.getProperty('SitchEnabled')
        Connections 
        {
            target: UM.ActiveTool;
            onPropertyChanged: 
            {
                stitch_button.enabled = UM.ActiveTool.getProperty('SitchEnabled')
            }
        }
        onClicked: 
        {
            UM.ActiveTool.triggerAction('stitchClouds')
        }
    }
}