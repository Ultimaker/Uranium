from unittest.mock import MagicMock

from UM.Controller import Controller
from UM.Event import ViewEvent, Event
from UM.Stage import Stage
from UM.View.View import View


def test_addView(application):
    controller = Controller(application)
    view_1 = View()
    view_1.setPluginId("test_1")
    view_2 = View()
    view_2.setPluginId("test_2")
    controller.viewsChanged.emit = MagicMock()
    controller.addView(view_1)

    assert controller.getAllViews() == {"test_1": view_1}
    assert controller.viewsChanged.emit.call_count == 1

    # Attempting to add the same view twice should not have any effect.
    controller.addView(view_1)
    assert controller.getAllViews() == {"test_1": view_1}
    assert controller.viewsChanged.emit.call_count == 1

    # It has the same ID (although the view is different). In that case it still shouldn't be added. 
    controller.addView(view_2)
    assert controller.getAllViews() == {"test_1": view_1}
    assert controller.viewsChanged.emit.call_count == 1


def test_getView(application):
    controller = Controller(application)
    view_1 = View()
    view_1.setPluginId("test_1")
    view_2 = View()
    view_2.setPluginId("test_2")

    controller.addView(view_1)
    controller.addView(view_2)

    assert controller.getView("test_1") == view_1
    assert controller.getView("test_2") == view_2
    assert controller.getView("NOPE") is None


def test_setActiveView(application):
    controller = Controller(application)
    view_1 = View()
    view_1.setPluginId("test_1")
    view_2 = View()
    view_2.setPluginId("test_2")

    controller.addView(view_1)
    controller.addView(view_2)
    controller.activeViewChanged.emit = MagicMock()

    # Attempting to set the view to a non existing one shouldn't do anything
    controller.setActiveView("blorp")
    assert controller.activeViewChanged.emit.call_count == 0

    view_1.event = MagicMock()
    controller.setActiveView("test_1")
    assert controller.activeViewChanged.emit.call_count == 1
    assert controller.getActiveView() == view_1
    # Ensure that the view gets notified that it was activated.
    assert view_1.event.call_args_list[0][0][0].type == Event.ViewActivateEvent

    controller.setActiveView("test_2")
    assert controller.getActiveView() == view_2
    assert controller.activeViewChanged.emit.call_count == 2
    # Ensure that the view was notified that it got deactivated again
    assert view_1.event.call_args_list[1][0][0].type == Event.ViewDeactivateEvent


def test_addStage(application):
    controller = Controller(application)
    stage_1 = Stage()
    stage_1.setPluginId("test_1")

    stage_2 = Stage()
    stage_2.setPluginId("test_1")
    controller.stagesChanged.emit = MagicMock()

    controller.addStage(stage_1)
    assert controller.stagesChanged.emit.call_count == 1
    assert controller.getAllStages() == {"test_1": stage_1}

    # Adding it again shouldn't influence anything
    controller.addStage(stage_1)
    assert controller.stagesChanged.emit.call_count == 1
    assert controller.getAllStages() == {"test_1": stage_1}

    # Adding a different stage (but with the same ID) should also not do anything!
    controller.addStage(stage_2)
    assert controller.stagesChanged.emit.call_count == 1
    assert controller.getAllStages() == {"test_1": stage_1}


