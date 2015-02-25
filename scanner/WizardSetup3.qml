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
            text: "<b>Position calibration board</b> <br> The calibration board needs to be placed in the centre of the camera view. Make sure that sufficient markers are visible. Ensure that ~80% of the image is filled up with the calibration board."
            wrapMode: Text.Wrap
            Layout.maximumWidth:parent.width
        }
        AnimatedImage
        {
            Layout.maximumWidth:parent.width
            source:"animatedPlaceholder.gif";
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
            UM.ToolbarData.setState(4);
        }
    }
}
