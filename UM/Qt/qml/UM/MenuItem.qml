import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import UM 1.5 as UM

MenuItem
{
    id: root

    property alias shortcut: _shortcut.sequence
    property bool indicatorVisible: root.icon.source.length > 0 || root.checkable
    height: visible ? UM.Theme.getSize("context_menu").height : 0
    property int contentWidth:
    {
        // This is the width of all the items in the contentItem except the filler
        return leftSpacer.width + label.width + middleSpacer.width + shortcutLabel.width + rightSpacer.width
    }

    Shortcut
    {
        id: _shortcut
        // If this menuItem has an action, the shortcut stuff is handled by the action (so this shortcut is disabled)
        // If only a shortcut is set, the menu item does need to handle it.
        // If both handle it at the same time, the action is only triggered half the time.
        enabled: root.action == null && root.enabled
        onActivated: root.triggered()
        context: Qt.ApplicationShortcut
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

    arrow: Image
    {
        source: UM.Theme.getIcon("ChevronSingleRight")
    }

    contentItem: RowLayout
    {
        spacing: 0
        opacity: root.enabled ? 1 : 0.5

        Item
        {
            // Left side margin
            id: leftSpacer
            width: root.indicatorVisible ? root.indicator.width + UM.Theme.getSize("default_margin").width : UM.Theme.getSize("default_margin").width
        }

        UM.Label
        {
            id: label
            text: replaceText(root.text)
            Layout.fillHeight:true
            elide: Label.ElideRight
            wrapMode: Text.NoWrap
        }

        Item
        {
            Layout.fillWidth: true
        }

        Item
        {
            // Middle margin
            id: middleSpacer
            width: visible ? UM.Theme.getSize("default_margin").width : 0
            visible: _shortcut.nativeText != "" || root.subMenu
        }

        UM.Label
        {
            id: shortcutLabel
            Layout.fillHeight: true
            text: _shortcut.nativeText
            color: UM.Theme.getColor("text_lighter")
        }

        Item
        {
            // Right side margin
            id: rightSpacer
            width: UM.Theme.getSize("default_margin").width
        }
    }
}
