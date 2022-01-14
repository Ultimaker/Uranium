import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import UM 1.5 as UM

MenuItem
{
    id: root

    property alias shortcut: _shortcut.sequence
    property bool indicatorVisible: root.icon.source.length > 0 || root.checkable
    height: visible ? implicitHeight : 0
    Shortcut
    {
        id: _shortcut
        // If this menuItem has an action, the shortcut stuff is handled by the action (so this shortcut is disabled)
        // If only a shortcut is set, the menu item does need to handle it.
        // If both handle it at the same time, the action is only triggered half the time.
        enabled: root.action == null && root.enabled
        onActivated: root.triggered()
        sequence: root.action != null ? root.action.shortcut: null
    }

    // Workaround for menu items in controls not supporting mnemonic shortcuts in all cases.
    // We use a seperate shortcut since we want the normal shortcut to be displayed to the right of the menu item
    // This shortcut needs to be "invisible"
    Shortcut
    {
        id: _mnemonicShortcut
        enabled: root.enabled
        onActivated: root.triggered()
    }

    function replaceText(txt)
    {
        var index = txt.indexOf("&")
        if(index >= 0)
        {
            txt = txt.replace(txt.substr(index, 2), "<u>" + txt.substr(index + 1, 1) + "</u>")
            _mnemonicShortcut.sequence = "Alt+" + txt.substr(index + 1, 1)
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
            width: root.indicatorVisible ? root.indicator.width + 2 * UM.Theme.getSize("narrow_margin").width : 0
        }

        UM.Label
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

        UM.Label
        {
            text: _shortcut.nativeText
            verticalAlignment: Qt.AlignVCenter
        }
    }
}
