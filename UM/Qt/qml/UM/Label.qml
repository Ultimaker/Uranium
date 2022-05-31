import QtQuick.Controls 2.15
import QtQuick 2.15
import UM 1.0 as UM

Label
{
    color: UM.Theme.getColor("text")
    font: UM.Theme.getFont("default")
    wrapMode: Text.Wrap
    renderType: Qt.platform.os == "osx" ? Text.QtRendering : Text.NativeRendering
    linkColor: UM.Theme.getColor("text_link")
    verticalAlignment: Text.AlignVCenter
}
