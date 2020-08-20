# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import enum

from UM.Settings.SettingDefinition import SettingDefinition


class RelationType(enum.IntEnum):
    """The type of relation, i.e. what direction does this relation have."""

    RequiresTarget = 1 # The relation represents that the owner requires the target.
    RequiredByTarget = 2 # The relation represents that the target requires the owner.


class SettingRelation:
    """A representation of a relationship between two settings.

    This is a simple class representing a relationship between two settings.
    One of the settings is the "owner", which means it contains the setting, the other
    setting is the "target", the setting the relation is pointing at. Relations
    have a type and a role. The type determines in what direction this relation is,
    the role what property it is used for.

    :note SettingRelation objects are usually created by DefinitionContainer after
    constructing SettingDefinition objects.
    """

    def __init__(self, owner: SettingDefinition, target: SettingDefinition, relation_type: RelationType, role: str) -> None:
        """Constructor.

        :param owner: :type{SettingDefinition} The object that owns this relation.
        :param target: :type{SettingDefinition} The target of the relation.
        :param type: :type{RelationType} The type of the relation.
        :param role: :type{string} The role of the relation, what property is it used for.
        """

        if owner is None or target is None:
            raise ValueError("owner or target cannot be None")

        self._owner = owner
        self._target = target
        self._type = relation_type
        self._role = role

    def __hash__(self):
        """Ensure that the SettingRelation is hashable, so it can be used in a set."""

        return hash(str(self))

    @property
    def owner(self) -> SettingDefinition:
        """The owner of this relation."""

        return self._owner

    @property
    def target(self) -> SettingDefinition:
        """
        The setting that this relation is relating with.
        """
        return self._target

    @property
    def type(self) -> RelationType:
        """The type of this relation."""

        return self._type

    @property
    def role(self) -> str:
        """The role of this relation."""

        return self._role

    def __repr__(self) -> str:
        return "<SettingRelation owner={0} target={1} type={2} role={3}>".format(self._owner, self._target, self._type, self._role)
