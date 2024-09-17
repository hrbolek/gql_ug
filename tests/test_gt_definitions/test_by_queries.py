from .gt_utils import (
    createByIdTest2,
    createUpdateTest2,
    createTest2
)

test_user_by_id = createByIdTest2(tableName="users")
# test_event_by_id = createByIdTest2(tableName="events")
test_user_page = createTest2(tableName="users", queryName="readp")
test_user_me = createTest2(tableName="users", queryName="me")
test_user_insert = createTest2(
    tableName="users", 
    queryName="create", 
    variables={
        "id": "aae16f75-e76e-43a7-b0bc-556f0f6dd29d",
        "name": "new event",
        # "type_id": "c0a12392-ae0e-11ed-9bd8-0242ac110002"
    })
# test_event_coverage = createTest2(
#     tableName="events", 
#     queryName="coverage")

test_user_update = createUpdateTest2(
    tableName="users", 
    variables={
        "id": "2d9dc5ca-a4a2-11ed-b9df-0242ac120003",
        "name": "user renamed"
    })
# test_event_delete = createTest2(
#     tableName="events",
#     queryName="delete",
#     variables={
#         "id": "9b642606-1551-4945-bc7d-ebb53cf513a7"
#     }
# )

test_group_by_id = createByIdTest2(tableName="groups")
test_group_page = createTest2(tableName="groups", queryName="readp")
test_group_insert = createTest2(
    tableName="groups", 
    queryName="create",
    variables={
        "id": "cdaf3926-1962-437c-8cb9-2167aa9e5a7d",
        "grouptype_id": "cd49e152-610c-11ed-9f29-001a7dda7110",
        "name": "new group",
        "name_en": "new group"
    }
)
test_group_update = createUpdateTest2(
    tableName="groups",
    variables={
        "id": "2d9dcd22-a4a2-11ed-b9df-0242ac120003",
        "name": "renamed"
    }
)
# test_group_delete = createTest2(
#     tableName="groups",
#     queryName="delete",
#     variables={
#         "id": "2d9dcd22-a4a2-11ed-b9df-0242ac120003"
#     }
# )

test_group_type_by_id = createByIdTest2(tableName="grouptypes")
test_group_type_page = createTest2(tableName="grouptypes", queryName="readp")
test_group_type_insert = createTest2(
    tableName="grouptypes", 
    queryName="create",
    variables={
        "id": "cdaf3926-1962-437c-8cb9-2167aa9e5a7d",
        "name": "new group type",
        "name_en": "new group type"
    }
)
test_group_type_update = createUpdateTest2(
    tableName="grouptypes",
    variables={
        "id": "cd49e152-610c-11ed-9f29-001a7dda7110",
        "name": "renamed"
    }
)
test_group_type_delete = createTest2(
    tableName="grouptypes",
    queryName="delete",
    variables={
        "id": "b1bedf72-931f-11ed-9b95-0242ac110002"
    }
)

test_group_category_by_id = createByIdTest2(tableName="groupcategories")
test_group_category_page = createTest2(tableName="groupcategories", queryName="readp")
test_group_category_insert = createTest2(
    tableName="groupcategories", 
    queryName="create",
    variables={
        "id": "4517678b-d564-438a-9a27-8e2a61018d46",
        "name": "new group category",
        "name_en": "new group category"
    }
)
test_group_category_update = createUpdateTest2(
    tableName="groupcategories",
    variables={
        "id": "be2b2dcc-4bfe-4035-99e8-dd6d6f01562e",
        "name": "renamed"
    }
)
test_group_category_delete = createTest2(
    tableName="groupcategories", 
    queryName="delete",
    variables={
        "id": "6b99de73-205a-41fc-9847-6f04fddc38f1",
    }
)

test_membership_by_id = createByIdTest2(tableName="memberships")
test_membership_page = createTest2(tableName="memberships", queryName="readp")
test_membership_insert = createTest2(
    tableName="memberships", 
    queryName="create",
    variables={
        "id": "181bf3b7-8a6d-4338-983c-14b1062d536a",
        "user_id": "89d1f638-ae0f-11ed-9bd8-0242ac110002",
        "group_id": "cd49e152-610c-11ed-9f29-001a7dda7110", 
    }
    )
test_membership_delete = createTest2(
    tableName="memberships",
    queryName="delete",
    variables={
        "id": "7cea8596-a4a2-11ed-b9df-0242ac120003"
    }
)

test_role_insert2 = createTest2(
    tableName="roles", 
    queryName="create",
    variables={
        "id": "181bf3b7-8a6d-4338-983c-14b1062d536a",
        "user_id": "89d1f638-ae0f-11ed-9bd8-0242ac110002",
        "group_id": "cd49e152-610c-11ed-9f29-001a7dda7110", 
        "roletype_id": "ced46aa4-3217-4fc1-b79d-f6be7d21c6b6"
    }

)
test_role_update2 = createUpdateTest2(
    tableName="roles",
    # queryName="update",
    variables={
        "id": "7cea8802-a4a2-11ed-b9df-0242ac120003", 
        "valid": False
    }
    )
test_role_delete = createTest2(
    tableName="roles",
    queryName="delete",
    variables={
        "id": "564b62f4-29f6-48b2-8bc8-ff52c800732a"
    }
)


test_role_type_by_id = createByIdTest2(tableName="roletypes")
test_role_type_page = createTest2(tableName="roletypes", queryName="readp")
test_role_type_insert = createTest2(
    tableName="roletypes",
    queryName="create",
    variables={
        "id": "ccede67c-8773-4109-b853-2319a1d06f83",
        "name": "new type",
        "name_en": "new type",
        "category_id": "774690a0-56b3-45d9-9887-0989ed3de4c0"
    }
)
test_role_type_update = createUpdateTest2(
    tableName="roletypes",
    variables={
        "id": "05a3e0f5-f71e-4caa-8012-229d868aa8ca",
        "name": "updated type name"
    }
)
test_role_type_delete = createTest2(
    tableName="roletypes",
    queryName="delete",
    variables={
        "id": "05a3e0f5-f71e-4caa-8012-229d868aa8ca",        
    }
)

test_role_category_by_id = createByIdTest2(tableName="rolecategories")
test_role_category_page = createTest2(tableName="rolecategories", queryName="readp")
test_role_category_insert = createTest2(
    tableName="rolecategories",
    queryName="create",
    variables={
        "id": "5da1480c-1123-4d35-8c0d-54b1c5acaa7b",
        "name": "new category",
        "name_en": "new category",
        "category_id": "774690a0-56b3-45d9-9887-0989ed3de4c0"
    }
)
test_role_category_update = createUpdateTest2(
    tableName="rolecategories",
    variables={
        "id": "fd73596b-1043-46f0-837a-baa0734d64df",
        "name": "updated category name"
    }
)
# test_role_category_delete = createTest2(
#     tableName="rolecategories",
#     queryName="delete",
#     variables={
#         "id": "094e70ad-9008-463b-8a01-04dd05a0e48c",        
#     }
# )

test_state_by_id = createByIdTest2(tableName="states")
test_state_page = createTest2(tableName="states", queryName="readp")
test_state_coverage = createTest2(tableName="states", queryName="coverage")
test_state_create = createTest2(
    tableName="states", 
    queryName="create",
    variables={
        "id": "6dee3e2f-9220-4825-b690-7b9d1b7a8a1d",
        "statemachine_id": "15257c8c-a259-46d3-993f-83d2a8d02b85",
        "name": "new state machine"
    }
    )
test_state_update = createUpdateTest2(
    tableName="states",
    variables={
        "id": "eb085919-640b-43f5-863d-2e69e4a86fe4",
        "name": "updated name"
    }
)
test_state_delete = createTest2(
    tableName="states",
    queryName="delete",
    variables={
        "id": "b44b9aef-d895-4ff5-a3ed-2f41ddc81f3a",
    }
)

test_statemachine_by_id = createByIdTest2(tableName="statemachines")
test_statemachine_page = createTest2(tableName="statemachines", queryName="readp")
test_statemachine_create = createTest2(
    tableName="statemachines", 
    queryName="create",
    variables={
        "id": "6278ca00-a975-435e-afac-62e31c884475",
        "name": "new state machine"
    }
    )
test_statemachine_update = createUpdateTest2(
    tableName="statemachines",
    variables={
        "id": "15257c8c-a259-46d3-993f-83d2a8d02b85",
        "name": "updated name"
    }
)
test_statemachine_delete = createTest2(
    tableName="statemachines", 
    queryName="delete",
    variables={
        "id": "2eea088a-ee0f-4bbd-b0dc-d86a48f0402d"
    }
)

test_statetransition_page = createTest2(tableName="statetransitions", queryName="readp")
test_statetransition_by_id = createByIdTest2(tableName="statetransitions")
test_statetransition_create = createTest2(
    tableName="statetransitions", 
    queryName="create",
    variables={
        "id": "078d9ae5-f8a6-47e6-a4ae-f527a49eb6a4",
        "statemachine_id": "15257c8c-a259-46d3-993f-83d2a8d02b85",
        "name": "new state transition",
        "source_id": "eb085919-640b-43f5-863d-2e69e4a86fe4",
        "target_id": "f9632f9a-cb18-4ca3-b71e-0e0c37cf334a",
    }
    )
test_statetransition_update = createUpdateTest2(
    tableName="statetransitions",
    variables={
        "id": "322cec6a-6c62-4611-8b67-a3b1532a9f17",
        "name": "updated name"
    }
)
test_statetransition_delete = createTest2(
    tableName="statetransitions", 
    queryName="delete",
    variables={
        "id": "322cec6a-6c62-4611-8b67-a3b1532a9f17"
    }
    )

test_roletypelist_by_id = createTest2(
    tableName="roletypelists",
    queryName="read",
    variables={
        "id": "c5056e8d-736a-4afb-aa7f-9ca626a19916"
    }
)

test_roletypelist_add_role = createTest2(
    tableName="roletypelists",
    queryName="addroletype",
    variables={
        "roletypelist_id": "c5056e8d-736a-4afb-aa7f-9ca626a19916",
        "roletype_id": "b87aed46-dfc3-40f8-ad49-03f4138c7478"
    }
)

test_roletypelist_remove_role = createTest2(
    tableName="roletypelists",
    queryName="removeroletype",
    variables={
        "roletypelist_id": "c5056e8d-736a-4afb-aa7f-9ca626a19916",
        "roletype_id": "ced46aa4-3217-4fc1-b79d-f6be7d21c6b6"
    }
)

test_rbac_user_by_id = createTest2(
    tableName="rbacs",
    queryName="read",
    variables={
        "id": "2d9dc868-a4a2-11ed-b9df-0242ac120003"
    }
)

test_rbac_group_by_id = createTest2(
    tableName="rbacs",
    queryName="read",
    variables={
        "id": "2d9dd1c8-a4a2-11ed-b9df-0242ac120003"
    }
)

test_rbac_coverage = createTest2(
    tableName="rbacs",
    queryName="coverage",
    variables={
        "id": "2d9dc868-a4a2-11ed-b9df-0242ac120003",
        "user_id": "2d9dc868-a4a2-11ed-b9df-0242ac120003"
    }
)

test_rbac_coverage2 = createTest2(
    tableName="rbacs",
    queryName="coverage",
    variables={
        "id": "2d9dd1c8-a4a2-11ed-b9df-0242ac120003",
        "user_id": "2d9dc868-a4a2-11ed-b9df-0242ac120003"
    }
)
