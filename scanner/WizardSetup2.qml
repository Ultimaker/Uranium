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
            text: "<b>Hardware setup</b> <br> Choose a hardware setup. We recommend choosing 'basic setup' if this is your first time using Argus."
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
            text: "Make sure all cables are attached well <br> and that everything is positioned in its slot"
            wrapMode: Text.Wrap
            Layout.maximumWidth:parent.width
        }
        Image
        {
            Layout.maximumWidth:parent.width
            source:"placeholder.png";
        }
    }
    buttons:NextButton
    {
        onClicked:
        {
            UM.ToolbarData.setState(3);
        }
    }
}
