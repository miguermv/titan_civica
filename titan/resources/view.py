from typing import Dict

from . import Resource
from .base import SchemaScoped
from ..props import (
    BoolProp,
    FlagProp,
    Props,
    QueryProp,
    StringProp,
    TagsProp,
)

from .column import Column


class View(Resource, SchemaScoped):
    """
    CREATE [ OR REPLACE ] [ SECURE ] [ { [ { LOCAL | GLOBAL } ] TEMP | TEMPORARY | VOLATILE } ] [ RECURSIVE ] VIEW [ IF NOT EXISTS ] <name>
      [ ( <column_list> ) ]
      [ <col1> [ WITH ] MASKING POLICY <policy_name> [ USING ( <col1> , <cond_col1> , ... ) ]
               [ WITH ] TAG ( <tag_name> = '<tag_value>' [ , <tag_name> = '<tag_value>' , ... ] ) ]
      [ , <col2> [ ... ] ]
      [ [ WITH ] ROW ACCESS POLICY <policy_name> ON ( <col_name> [ , <col_name> ... ] ) ]
      [ [ WITH ] TAG ( <tag_name> = '<tag_value>' [ , <tag_name> = '<tag_value>' , ... ] ) ]
      [ COPY GRANTS ]
      [ COMMENT = '<string_literal>' ]
      AS <select_statement>
    """

    resource_type = "VIEW"
    props = Props(
        secure=FlagProp("secure"),
        # columns=ResourceListProp(Column),
        volatile=FlagProp("volatile"),
        recursive=FlagProp("recursive"),
        tags=TagsProp(),
        change_tracking=BoolProp("change_tracking"),
        copy_grants=FlagProp("copy grants"),
        comment=StringProp("comment"),
        as_=QueryProp("as"),
    )

    name: str
    owner: str = "SYSADMIN"

    secure: bool = False
    volatile: bool = False
    recursive: bool = False
    columns: list = []
    tags: Dict[str, str] = None
    change_tracking: bool = None
    copy_grants: bool = None
    comment: str = None
    as_: str = None
