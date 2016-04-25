# Copyright (c) 2016 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import enum

##  A representation of a relationship between two settings.
#
#   This is a simple class representing a relationship between two settings.
#   One of the settings is the "owner", which means it contains the setting, the other
#   setting is the "target", the setting the relation is pointing at. Relations
#   have a type and a role. The type determines in what direction this relation is,
#   the role what it is used for.
#
#   \note SettingRelation objects are usually created by DefinitionContainer after
#   constructing SettingDefinition objects.
class SettingRelation:
    ##  The type of relation, i.e. what direction does this relation have.
    class RelationType(enum.IntEnum):
        RequiresTarget = 1 # The relation represents that the owner requires the target.
        RequiredByTarget = 2 # The relation represents that the target requires the owner.

    ##  The role of the relation, i.e. what is it used for.
    class RelationRole(enum.IntEnum):
        Value = 1 # The relation is used to calculate the setting value.
        Minimum = 2 # The relation is used to calculate the minimum.
        Maximum = 3 # The relation is used to calculate the maximum.
        MinimumWarning = 4 # The relation is used to calculate the minimum warning.
        MaximumWarning = 5 # The relation is used to calculate the maximum warning.
        Enabled = 6 # The relation is used to determine whether the setting is enabled or not.
        Other = 7 # The relation is used for something application-defined.

    ##  Constructor.
    #
    #   \param owner \type{SettingDefinition} The object that owns this relation.
    #   \param target \type{SettingDefinition} The target of the relation.
    #   \param type \type{RelationType} The type of the relation.
    #   \param role \type{RelationRole} The role of the relation.
    def __init__(self, owner, target, relation_type, role):
        if owner is None or target is None:
            raise ValueError("owner or target cannot be None")

        self._owner = owner
        self._target = target
        self._type = relation_type
        self._role = role

    ##  The owner of this relation.
    @property
    def owner(self):
        return self._owner

    ##  The target of this relation.
    @property
    def target(self):
        return self._target

    ##  The type of this relation.
    @property
    def type(self):
        return self._type

    ##  The role of this relation.
    @property
    def role(self):
        return self._role
