import strawberry

from .groupGQLModel import GroupQueries
from .userGQLModel import UserQueries
from .roleGQLModel import RoleQueries
from .groupTypeGQLModel import GroupTypeQueries
from .roleTypeGQLModel import RoleTypeQueries
from .stateGQLModel import (
    StateMachineQueries,
    StateQueries,
    StateTransitionsQueries)

@strawberry.type(description="""Type for query root""")
class Query(
    GroupQueries, 
    GroupTypeQueries,
    UserQueries, 
    RoleQueries,
    RoleTypeQueries,    
    StateMachineQueries,
    StateQueries,
    StateTransitionsQueries):


    from .roleCategoryGQLModel import role_category_by_id, role_category_page
    # role_category_by_id = role_category_by_id

    # from .roleCategoryGQLModel import role_category_page
    # role_category_page = role_category_page

    from .groupCategoryGQLModel import (
        group_category_by_id, 
        group_category_page
    )

    from .RBACObjectGQLModel import rbac_by_id
    # rbac_by_id = rbac_by_id

    from .membershipGQLModel import (
        membership_page,
        membership_by_id
    )
    # membership_page = membership_page
    # membership_by_id = membership_by_id

    from .roleListGQLModel import role_type_list_by_id
    # role_type_list_by_id = role_type_list_by_id

