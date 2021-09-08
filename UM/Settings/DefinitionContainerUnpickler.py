import pickle

safe_globals = {
    "UM.Settings.DefinitionContainer.DefinitionContainer",
    "collections.OrderedDict",
    "UM.Settings.SettingDefinition.SettingDefinition",
    "UM.Settings.SettingFunction.SettingFunction",
    "UM.Settings.SettingRelation.SettingRelation",
    "UM.Settings.SettingRelation.RelationType"
}


class DefinitionContainerUnpickler(pickle.Unpickler):
    """
    Pickle by itself is not safe at all. We can't use any kind of signing, since the code itself is open (and at that
    point it would be trivially easy to read the secret used to sign it).

    What we can do is simply whitelist the things that the DefinitionContainer needs (and prevent everything else!)

    This obviously only protects against malicious cache files where the attacker (or user) can't modify the python
    files. This is common for setups where users don't have admin permission or have other more strict restrictions.
    """
    def find_class(self, module, name):
        if module + "." + name in safe_globals:
            return super().find_class(module, name)

        # Raise exception for everything that isn't in the safe list.
        raise pickle.UnpicklingError(f"global '{module}.{name}' is forbidden")
