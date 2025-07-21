import strawberry
import typing

from .groupGQLModel import GroupMutations
from .groupTypeGQLModel import GroupTypeMutations
from .userGQLModel import UserMutations
from .roleGQLModel import RoleMutations
from .roleTypeGQLModel import RoleTypeMutations
from .membershipGQLModel import MembershipMutations

from .stateGQLModel import (
    StateMutations,
    StateMachineMutations,
    StateTransitionMutations
)
@strawberry.type
class Mutation(
    GroupMutations, 
    GroupTypeMutations,
    UserMutations,
    MembershipMutations,
    RoleMutations,
    RoleTypeMutations,
    StateMutations,
    StateMachineMutations,
    StateTransitionMutations):


    # from .membershipGQLModel import (
    #     membership_insert,
    #     membership_update,
    #     membership_delete
    # )
    # membership_insert = membership_insert
    # membership_update = membership_update
    # membership_delete = membership_delete
    
    from .deprecated.roleCategoryGQLModel import (
        role_category_insert,
        role_category_update,
        role_category_delete
    )
    # role_category_insert = role_category_insert
    # role_category_update = role_category_update
    # role_category_delete = role_category_delete

    # from .groupCategoryGQLModel import (
    #     group_category_insert,
    #     group_category_update,
    #     group_category_delete
    # )
    # group_category_insert = group_category_insert
    # group_category_update = group_category_update
    # group_category_delete = group_category_delete

    from .roleListGQLModel import (
        role_type_list_add as role_type_list_add_role,
        role_type_list_remove as role_type_list_remove_role
    )
    # role_type_list_add_role = role_type_list_add
    # role_type_list_remove_role = role_type_list_remove
