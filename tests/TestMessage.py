from UM.Message import Message


def test_addAction():
    message = Message()
    message.addAction(action_id = "blarg", name = "zomg", icon = "NO ICON", description="SuperAwesomeMessage")

    assert len(message.getActions()) == 1


def test_gettersAndSetters():
    message = Message(text = "OMG", title="YAY", image_caption="DERP", image_source= "HERP", option_text="FOO", option_state= False)
    message.setMaxProgress(200)
    assert message.getText() == "OMG"
    assert message.getTitle() == "YAY"
    assert message.getImageCaption() == "DERP"
    assert message.getImageSource() == "HERP"
    assert message.getOptionText() == "FOO"
    assert message.getMaxProgress() == 200
    assert message.getOptionState() == False

    message.setTitle("whoo")
    assert message.getTitle() == "whoo"


def test_dismissable():
    # In certain conditions the message is always set to dismissable (even if we asked for a non dimissiable message)
    message = Message(lifetime=0, dismissable=False)
    assert message.isDismissable()


