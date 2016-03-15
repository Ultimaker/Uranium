import QtQuick 2.4
import QtQuick.Controls.Private 1.0

// TooltipArea.qml
// This file contains private Qt Quick modules that might change in future versions of Qt
// Tested on: Qt 5.4.1
// Based on https://www.kullo.net/blog/tooltiparea-the-missing-tooltip-component-of-qt-quick/

MouseArea {
    id: _root
    property string text: ""

    hoverEnabled: _root.enabled

    onExited: Tooltip.hideText()
    onCanceled: Tooltip.hideText()

    Timer {
        interval: 1000
        running: _root.enabled && _root.containsMouse && _root.text.length
        onTriggered: Tooltip.showText(_root, Qt.point(_root.mouseX, _root.mouseY), wrapText(_root.text, 80))
    }

    /**
     * Manually wrap a line of text to a certain maximum line length.
     *
     * This method will introduce newlines so that the length of each string
     * will be equal or less than a certain maximum line length.
     *
     * \param text The text to wrap.
     * \param line_length The maximum line length to wrap to.
     */
    function wrapText(text, line_length)
    {
        var words = text.split(" ");
        var lines = [];
        var line = "";
        var word = "";

        for(var i = 0; i < words.length; i++)
        {
            word = words[i];
            if((line.length + word.length + 1) > line_length)
            {
                lines.push(line);
                line = "";
            }
            line += " "
            line += word
        }
        lines.push(line);
        return lines.join("\n");
    }
}
