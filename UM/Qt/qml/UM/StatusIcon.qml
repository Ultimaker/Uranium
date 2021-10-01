// Copyright (c) 2021 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.7
import QtQuick.Controls 2.3

import UM 1.2 as UM

Item
{
    enum Status {
        POSITIVE,
        NEUTRAL,
        WARNING,
        ERROR,
        CLOUD
    }
    property string status: StatusIcon.Status.NEUTRAL

    height: width
    UM.RecolorImage
    {
        id: iconBackground
        height: source != "" ? parent.height : 0
        width: height
        sourceSize.width: width
        sourceSize.height: height
        source: ""
        color: "transparent"
    }
    UM.RecolorImage
    {
        id: iconInner
        height: source != "" ? parent.height : 0
        width: height
        sourceSize.width: width
        sourceSize.height: height
        source: ""
        color: "transparent"
    }

    states:
    [
        State
        {
            name: "positive"
            when: status == StatusIcon.Status.POSITIVE
            PropertyChanges
            {
                target: iconInner
                source: UM.Theme.getIcon("Check", "low")
                color: UM.Theme.getColor("message_success_icon")
            }
            PropertyChanges
            {
                target: iconBackground
                source: UM.Theme.getIcon("CircleSolid", "low")
                color: UM.Theme.getColor("success")
            }
        },
        State
        {
            name: "neutral"
            when: status == StatusIcon.Status.NEUTRAL
            PropertyChanges
            {
                target: iconInner
                source: ""
                color: "transparent"
            }
            PropertyChanges
            {
                target: iconBackground
                source: ""
                color: "transparent"
            }
        },
        State
        {
            name: "warning"
            when: status == StatusIcon.Status.WARNING
            PropertyChanges
            {
                target: iconInner
                source: UM.Theme.getIcon("Warning", "low")
                color: UM.Theme.getColor("message_warning_icon")
            }
            PropertyChanges
            {
                target: iconBackground
                source: UM.Theme.getIcon("CircleSolid", "low")
                color: UM.Theme.getColor("warning")
            }
        },
        State
        {
            name: "error"
            when: status == StatusIcon.Status.ERROR
            PropertyChanges
            {
                target: iconInner
                source: UM.Theme.getIcon("Cancel", "low")
                color: UM.Theme.getColor("message_error_icon")
            }
            PropertyChanges
            {
                target: iconBackground
                source: UM.Theme.getIcon("CircleSolid", "low")
                color: UM.Theme.getColor("error")
            }
        },
        State
        {
            name: "cloud"
            when: status == StatusIcon.Status.CLOUD
            PropertyChanges
            {
                target: iconInner
                source: UM.Theme.getIcon("CloudBadge", "low")
                color: UM.Theme.getColor("primary")
            }
            PropertyChanges
            {
                target: iconBackground
                source: ""
            }
        }
    ]
}
