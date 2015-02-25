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
            id:introText1
            text: "<b>Camera Exposure</b>"
            wrapMode: Text.Wrap
            Layout.maximumWidth:parent.width
        }
        
        Image
        {
            Layout.maximumWidth:parent.width
            source:"placeholder.png";
        }
    }
    buttons: NextButton
    {
        onClicked:
        {
            UM.ToolbarData.setState(7);
        }
    }
}
