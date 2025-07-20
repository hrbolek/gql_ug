import strawberry

from .groupGQLModel import GroupQueries
from .userGQLModel import UserQueries
from .roleGQLModel import RoleQueries
from .groupTypeGQLModel import GroupTypeQueries
@strawberry.type(description="""Type for query root""")
class Query(
    GroupQueries, 
    GroupTypeQueries,
    UserQueries, 
    RoleQueries):


    from .roleTypeGQLModel import role_type_by_id, role_type_page
    # role_type_by_id = role_type_by_id

    # from .roleTypeGQLModel import role_type_page
    # role_type_page = role_type_page

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

    from .stateGQLModel import (
        state_by_id,
        state_page,


        statemachine_by_id,
        statemachine_page,

        statetransition_page,
        statetransition_by_id
        # statec
    )

    # state_by_id = state_by_id
    # state_page = state_page

    # statemachine_by_id = statemachine_by_id
    # statemachine_page = statemachine_page

    # statetranstition_page = statetransition_page
    # statetransition_by_id = statetransition_by_id