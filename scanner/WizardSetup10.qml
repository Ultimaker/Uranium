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
        Label
        {
            id:introText1
            text: "<b>Scan object</b> <br> You're now scanning."
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
            UM.ToolbarData.setState(11);
        }
    }
}
