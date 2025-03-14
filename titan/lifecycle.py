import sys

from inflection import pluralize

from .builder import tidy_sql
from .enums import ResourceType
from .identifiers import URN, FQN
from .props import Props
from .resource_name import ResourceName

__this__ = sys.modules[__name__]


def fqn_to_sql(fqn: FQN):
    database = f"{ResourceName(fqn.database)}." if fqn.database else ""
    schema = f"{ResourceName(fqn.schema)}." if fqn.schema else ""
    name = ResourceName(fqn.name)
    return f"{database}{schema}{name}"


################ Create functions


def create_resource(urn: URN, data: dict, props: Props, if_not_exists: bool = False) -> str:
    return getattr(__this__, f"create_{urn.resource_label}", create__default)(urn, data, props, if_not_exists)


def create__default(urn: URN, data: dict, props: Props, if_not_exists: bool = False) -> str:
    return tidy_sql(
        "CREATE",
        urn.resource_type,
        "IF NOT EXISTS" if if_not_exists else "",
        fqn_to_sql(urn.fqn),
        props.render(data),
    )


def create_account_parameter(urn: URN, data: dict, props: Props, if_not_exists: bool = False) -> str:
    value = data["value"]
    if isinstance(value, str):
        value = f"'{value}'"
    return tidy_sql(
        "ALTER",
        "ACCOUNT",
        "SET",
        urn.fqn.name,
        "=",
        value,
    )


def create_aggregation_policy(urn: URN, data: dict, props: Props, if_not_exists: bool = False) -> str:
    return tidy_sql(
        "CREATE",
        "AGGREGATION POLICY",
        "IF NOT EXISTS" if if_not_exists else "",
        fqn_to_sql(urn.fqn),
        "AS () RETURNS AGGREGATION_CONSTRAINT",
        props.render(data),
    )


def create_database(urn: URN, data: dict, props: Props, if_not_exists: bool = False) -> str:
    data = data.copy()
    transient = data.pop("transient", None)
    return tidy_sql(
        "CREATE",
        "TRANSIENT" if transient else "",
        urn.resource_type,
        "IF NOT EXISTS" if if_not_exists else "",
        urn.fqn,
        props.render(data),
    )


def create_database_role_grant(urn: URN, data: dict, props: Props, if_not_exists: bool = False) -> str:
    if data["to_role"] is not None:
        to = data["to_role"]
        to_type = "ROLE"
    else:
        to = data["to_database_role"]
        to_type = "DATABASE ROLE"

    return tidy_sql(
        "GRANT",
        "DATABASE ROLE",
        data["database_role"],
        "TO",
        to_type,
        to,
    )


def create_function(urn: URN, data: dict, props: Props, if_not_exists: bool = False) -> str:
    db = f"{urn.fqn.database}." if urn.fqn.database else ""
    schema = f"{urn.fqn.schema}." if urn.fqn.schema else ""
    name = f"{db}{schema}{data['name']}"
    return tidy_sql(
        "CREATE",
        urn.resource_type,
        "IF NOT EXISTS" if if_not_exists else "",
        name,
        props.render(data),
    )


def create_future_grant(urn: URN, data: dict, props: Props, if_not_exists: bool):
    on_type = data["on_type"]
    if "INTEGRATION" in on_type:
        on_type = "INTEGRATION"
    return tidy_sql(
        "GRANT",
        data["priv"],
        "ON FUTURE",
        pluralize(on_type).upper(),
        "IN",
        data["in_type"],
        data["in_name"],
        "TO",
        data["to_type"],
        data["to"],
    )


def create_grant(urn: URN, data: dict, props: Props, if_not_exists: bool):
    on_type = data["on_type"]
    if "INTEGRATION" in str(on_type):
        on_type = "INTEGRATION"
    elif on_type == "ACCOUNT":
        on_type = ""
    return tidy_sql(
        "GRANT",
        data["priv"],
        "ON",
        on_type,
        data["on"],
        "TO",
        data["to_type"],
        data["to"],
        "WITH GRANT OPTION" if data["grant_option"] else "",
    )


def create_grant_on_all(urn: URN, data: dict, props: Props, if_not_exists: bool):
    sql_parts = [
        "GRANT",
        data["priv"],
        "ON ALL",
        pluralize(data["on_type"]),
        "IN",
        data["in_type"],
        data["in_name"],
        "TO",
        data["to_type"],
        data["to"],
        "COPY CURRENT GRANTS" if data.get("copy_current_grants") else None,
    ]
    
    return tidy_sql(*sql_parts)


def create_masking_policy(urn: URN, data: dict, props: Props, if_not_exists: bool = False) -> str:
    return tidy_sql(
        "CREATE",
        urn.resource_type,
        "IF NOT EXISTS" if if_not_exists else "",
        urn.fqn,
        "AS",
        props.render(data),
    )


def create_procedure(urn: URN, data: dict, props: Props, if_not_exists: bool = False) -> str:
    if if_not_exists:
        raise Exception("IF NOT EXISTS not supported for CREATE PROCEDURE")
    db = f"{urn.fqn.database}." if urn.fqn.database else ""
    schema = f"{urn.fqn.schema}." if urn.fqn.schema else ""
    name = f"{db}{schema}{urn.fqn.name}"
    return tidy_sql(
        "CREATE",
        urn.resource_type,
        name,
        props.render(data),
    )


def create_role_grant(urn: URN, data: dict, props: Props, if_not_exists: bool = False):
    if data["to_role"] is not None:
        to = data["to_role"]
        to_type = "ROLE"
    else:
        to = data["to_user"]
        to_type = "USER"
    return tidy_sql(
        "GRANT",
        "ROLE",
        data["role"],
        "TO",
        to_type,
        to,
    )


def create_scanner_package(urn: URN, data: dict, props: Props, if_not_exists: bool = False) -> str:
    package_name = f"'{urn.fqn.name}'"
    return tidy_sql(
        "CALL SNOWFLAKE.TRUST_CENTER.SET_CONFIGURATION(",
        "'ENABLED',",
        "'TRUE',",
        package_name,
        ")",
    )


def create_schema(urn: URN, data: dict, props: Props, if_not_exists: bool = False) -> str:
    data = data.copy()
    transient = data.pop("transient", None)
    return tidy_sql(
        "CREATE",
        "TRANSIENT" if transient else "",
        urn.resource_type,
        "IF NOT EXISTS" if if_not_exists else "",
        urn.fqn,
        props.render(data),
    )


def create_table(urn: URN, data: dict, props: Props, if_not_exists: bool = False) -> str:
    data = data.copy()
    transient = data.pop("transient", None)
    return tidy_sql(
        "CREATE",
        "TRANSIENT" if transient else "",
        urn.resource_type,
        "IF NOT EXISTS" if if_not_exists else "",
        urn.fqn,
        props.render(data),
    )


def create_tag_reference(urn: URN, data: dict, props: Props, if_not_exists: bool = False) -> str:
    tags_sql = ", ".join([f"{k}='{v}'" for k, v in data["tags"].items()])
    return tidy_sql(
        "ALTER",
        data["object_domain"],
        data["object_name"],
        "SET TAG",
        tags_sql,
    )


def create_view(urn: URN, data: dict, props: Props, if_not_exists: bool = False) -> str:
    data = data.copy()
    secure = data.pop("secure", None)
    volatile = data.pop("volatile", None)
    recursive = data.pop("recursive", None)
    return tidy_sql(
        "CREATE",
        "SECURE" if secure else "",
        "VOLATILE" if volatile else "",
        "RECURSIVE" if recursive else "",
        urn.resource_type,
        "IF NOT EXISTS" if if_not_exists else "",
        urn.fqn,
        props.render(data),
    )


################ Update functions


def update_resource(urn: URN, data: dict, props: Props) -> str:
    return getattr(__this__, f"update_{urn.resource_label}", update__default)(urn, data, props)


def update__default(urn: URN, data: dict, props: Props) -> str:
    attr, new_value = data.popitem()
    attr = attr.lower()
    if new_value is None:
        return tidy_sql("ALTER", urn.resource_type, urn.fqn, "UNSET", attr)
    elif attr == "name":
        return tidy_sql("ALTER", urn.resource_type, urn.fqn, "RENAME TO", new_value)
    elif attr == "owner":
        raise NotImplementedError
    else:
        return tidy_sql(
            "ALTER",
            urn.resource_type,
            urn.fqn,
            "SET",
            props.render({attr: new_value}),
        )


def update_account_parameter(urn: URN, data: dict, props: Props) -> str:
    return create_account_parameter(urn, data, props)


def update_event_table(urn: URN, data: dict, props: Props) -> str:
    new_urn = URN(ResourceType.TABLE, urn.fqn, urn.account_locator)
    return update__default(new_urn, data, props)


def update_procedure(urn: URN, data: dict, props: Props) -> str:
    if "execute_as" in data:
        return tidy_sql(
            "ALTER",
            urn.resource_type,
            urn.fqn,
            "EXECUTE AS",
            data["execute_as"],
        )
    else:
        return update__default(urn, data, props)


def update_role_grant(urn: URN, data: dict, props: Props) -> str:
    raise NotImplementedError


def update_scanner_package(urn: URN, data: dict, props: Props) -> str:
    package_name = f"'{urn.fqn.name}'"
    attr, new_value = data.popitem()
    if attr == "schedule":
        new_value = f"'USING CRON {new_value}'"
    else:
        new_value = f"'{new_value}'"
    return tidy_sql(
        "CALL SNOWFLAKE.TRUST_CENTER.SET_CONFIGURATION(",
        f"'{attr}',",
        new_value,
        ",",
        package_name,
        ")",
    )


def update_schema(urn: URN, data: dict, props: Props) -> str:
    attr, new_value = data.popitem()
    attr = attr.lower()
    if new_value is None:
        return tidy_sql("ALTER SCHEMA", urn.fqn, "UNSET", attr)
    elif attr == "name":
        return tidy_sql("ALTER SCHEMA", urn.fqn, "RENAME TO", new_value)
    elif attr == "owner":
        raise NotImplementedError
    elif attr == "transient":
        raise Exception("Cannot change transient property of schema")
    elif attr == "managed_access":
        return tidy_sql("ALTER SCHEMA", urn.fqn, "ENABLE" if new_value else "DISABLE", "MANAGED ACCESS")
    else:
        new_value = f"'{new_value}'" if isinstance(new_value, str) else new_value
        return tidy_sql("ALTER SCHEMA", urn.fqn, "SET", attr, "=", new_value)


def update_table(urn: URN, data: dict, props: Props) -> str:
    attr, new_value = data.popitem()
    attr = attr.lower()
    if attr == "columns":
        raise NotImplementedError(data)
    else:
        return update__default(urn, {attr: new_value}, props)


# FIXME
# The AFTER attribute on tasks is one of the only attributes that is stateful,
# which means that you need to know the current value in order to modify it.
# This is a problem because we don't have a concept of "current value" for lifecycle updates
# and so we can't know what value to set.
def update_task(urn: URN, data: dict, props: Props) -> str:
    attr, new_value = data.popitem()
    attr = attr.lower()
    if attr == "as_":
        return tidy_sql("ALTER TASK", urn.fqn, "MODIFY", "AS", new_value)
    # elif attr == "after":
    #     if new_value is None:
    #         return tidy_sql("ALTER TASK", urn.fqn, "MODIFY", "AFTER", "NONE")
    #     else:
    #         return tidy_sql("ALTER TASK", urn.fqn, "MODIFY", "AFTER", ",".join([f"'{name}'" for name in new_value]))
    elif attr == "when":
        if new_value is None:
            return tidy_sql("ALTER TASK", urn.fqn, "REMOVE", "WHEN")
        else:
            return tidy_sql("ALTER TASK", urn.fqn, "MODIFY", "WHEN", new_value)
    elif attr == "state":
        change_verb = "RESUME" if new_value == "STARTED" else "SUSPEND"
        return tidy_sql("ALTER TASK", urn.fqn, change_verb)
    else:
        return update__default(urn, {attr: new_value}, props)


def update_iceberg_table(urn: URN, data: dict, props: Props) -> str:
    attr, new_value = data.popitem()
    attr = attr.lower()
    if attr == "columns":
        raise NotImplementedError(data)
    else:
        return update__default(urn, {attr: new_value}, props)


################ Drop functions


def drop_resource(urn: URN, data: dict, if_exists: bool = False) -> str:
    return getattr(__this__, f"drop_{urn.resource_label}", drop__default)(urn, data, if_exists=if_exists)


def drop__default(urn: URN, data: dict, if_exists: bool) -> str:
    return tidy_sql(
        "DROP",
        urn.resource_type,
        "IF EXISTS" if if_exists else "",
        fqn_to_sql(urn.fqn),
    )


def drop_account_parameter(urn: URN, data: dict, if_exists: bool) -> str:
    return tidy_sql(
        "ALTER",
        "ACCOUNT",
        "UNSET",
        urn.fqn.name,
    )


def drop_database(urn: URN, data: dict, if_exists: bool) -> str:
    return tidy_sql(
        "DROP",
        urn.resource_type,
        "IF EXISTS" if if_exists else "",
        urn.fqn,
        "RESTRICT",
    )


def drop_database_role_grant(urn: URN, data: dict, **kwargs):

    from_type = "ROLE" if data["to_role"] else "DATABASE ROLE"
    from_name = data["to_role"] if data["to_role"] else data["to_database_role"]

    return tidy_sql(
        "REVOKE DATABASE ROLE",
        ResourceName(data["database_role"]),
        "FROM",
        from_type,
        ResourceName(from_name),
    )


def drop_function(urn: URN, data: dict, if_exists: bool) -> str:
    return tidy_sql(
        "DROP",
        urn.resource_type,
        "IF EXISTS" if if_exists else "",
        urn.fqn,
    )


def drop_future_grant(urn: URN, data: dict, **kwargs):
    return tidy_sql(
        "REVOKE",
        data["priv"],
        "ON FUTURE",
        pluralize(data["on_type"]).upper(),
        "IN",
        data["in_type"],
        data["in_name"],
        "FROM",
        data["to"],
        # props.render(data), #TODO grant option
    )


def drop_grant(urn: URN, data: dict, **kwargs):
    if data["priv"] == "OWNERSHIP":
        raise NotImplementedError
    return tidy_sql(
        "REVOKE",
        data["priv"],
        "ON",
        data["on_type"],
        data["on"] if data["on_type"] != "ACCOUNT" else "",
        "FROM",
        data["to"],
        # "CASCADE" if cascade else "RESTRICT",
    )


def drop_grant_on_all(urn: URN, data: dict, **kwargs):
    return tidy_sql(
        "REVOKE",
        data["priv"],
        "ON ALL",
        data["on_type"],
        "IN",
        data["in_type"],
        data["in_name"],
    )


def drop_procedure(urn: URN, data: dict, if_exists: bool) -> str:
    return tidy_sql(
        "DROP",
        urn.resource_type,
        "IF EXISTS" if if_exists else "",
        urn.fqn,
        # data["returns"],
    )


def drop_role_grant(urn: URN, data: dict, **kwargs):
    return tidy_sql(
        "REVOKE ROLE",
        ResourceName(data["role"]),
        "FROM",
        "ROLE" if data.get("to_role") else "USER",
        ResourceName(data["to_role"] if data.get("to_role") else data["to_user"]),
    )


def drop_scanner_package(urn: URN, data: dict, **kwargs) -> str:
    package_name = f"'{urn.fqn.name}'"
    return tidy_sql(
        "CALL SNOWFLAKE.TRUST_CENTER.SET_CONFIGURATION(",
        "'ENABLED',",
        "'FALSE',",
        package_name,
        ")",
    )


################ Transfer functions


def transfer_resource(
    urn: URN,
    owner: str,
    owner_resource_type: ResourceType,
    copy_current_grants: bool = False,
    revoke_current_grants: bool = False,
) -> str:
    return getattr(__this__, f"transfer_{urn.resource_label}", transfer__default)(
        urn,
        owner,
        owner_resource_type,
        copy_current_grants,
        revoke_current_grants,
    )


def transfer__default(
    urn: URN,
    owner: str,
    owner_resource_type: ResourceType,
    copy_current_grants: bool = False,
    revoke_current_grants: bool = False,
) -> str:
    return tidy_sql(
        "GRANT OWNERSHIP ON",
        urn.resource_type,
        urn.fqn,
        "TO",
        owner_resource_type,
        owner,
        "REVOKE CURRENT GRANTS" if revoke_current_grants else "",
        "COPY CURRENT GRANTS" if copy_current_grants else "",
    )
