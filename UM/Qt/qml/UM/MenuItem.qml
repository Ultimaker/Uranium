import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import UM 1.5 as UM

MenuItem
{
    id: root

    property alias shortcut: _shortcut.sequence
    property bool indicatorVisible: root.icon.source.length > 0 || root.checkable

    Shortcut
    {
        id: _shortcut
        enabled: root.enabled
        onActivated: root.triggered()
        sequence: root.action != null ? root.action.shortcut: null
    }

    function replaceText(txt)
    {
        var index = txt.indexOf("&")
        if(index >= 0)
        {
            txt = txt.replace(txt.substr(index, 2), "<u>" + txt.substr(index + 1, 1) + "</u>")
        }
        return txt
    }

    contentItem: RowLayout
    {
        spacing: 0
        width: root.width
        opacity: root.enabled ? 1 : 0.5

        Item
        {
            // Spacer
            width: root.indicatorVisible ? root.indicator.width + UM.Theme.getSize("narrow_margin").width : 0
        }

        Label
        {
            text: replaceText(root.text)
            Layout.fillWidth: true
            elide: Label.ElideRight
            verticalAlignment: Qt.AlignVCenter
        }

        Item
        {
            Layout.fillWidth: true
        }

        Label
        {
            text: _shortcut.nativeText
            verticalAlignment: Qt.AlignVCenter
        }
    }
}
