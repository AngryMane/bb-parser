from typing import List, Optional

from collections import namedtuple
from xml.etree.ElementInclude import include

from pkg_resources import require

Position = namedtuple("Position", ["lineno", "pos"])
FunctionHeader = namedtuple(
    "FunctionInfo", ["name", "raw_text", "start", "end", "is_python", "is_fakeroot"]
)
FunctionBody = namedtuple("FunctionBody", ["raw_text", "start", "end"])
SymbolInfo = namedtuple("TaskInfo", ["name", "start", "end"])
VariableInfo = namedtuple(
    "VariableInfo", ["name", "start", "end", "is_append", "is_prepend"]
)
OperatorInfo = namedtuple(
    "OperatorInfo",
    ["is_immediate_expand", "is_weak", "is_weak_weak", "is_predot", "is_postdot"],
)


class BitbakeVisitorBase:
    def __init__(self: "BitbakeVisitorBase") -> None:
        pass

    # Bitbake parser events
    def function_callback(
        self: "BitbakeVisitorBase",
        file_path: str,
        head: FunctionHeader,
        body: FunctionBody,
    ):
        pass

    def python_function_callback(
        self: "BitbakeVisitorBase",
        file_path: str,
        head: FunctionHeader,
        body: FunctionBody,
    ):
        pass

    def export_function_callback(
        self: "BitbakeVisitorBase",
        file_path: str,
        function_name: str,
        start: Position,
        end: Position,
    ):
        pass

    def add_task_callback(
        self: "BitbakeVisitorBase",
        file_path: str,
        added_task: SymbolInfo,
        before: List[SymbolInfo],
        after: List[SymbolInfo],
    ):
        pass

    def delete_task_callback(
        self: "BitbakeVisitorBase", file_path: str, deleted_task: SymbolInfo
    ):
        pass

    def add_handler_callback(
        self: "BitbakeVisitorBase", file_path: str, handler_task: SymbolInfo
    ):
        pass

    def inherit_callback(
        self: "BitbakeVisitorBase",
        file_path: str,
        inherit_target_names: List[SymbolInfo],
    ):
        pass

    # Conf parser events
    def config_callback(
        self: "BitbakeVisitorBase",
        file_path: str,
        is_export: bool,
        variable: VariableInfo,
        flag: Optional[SymbolInfo],
        operator: OperatorInfo,
        value: SymbolInfo,
    ) -> None:
        pass

    def include_callback(
        self: "BitbakeVisitorBase", file_path: str, include_target: SymbolInfo
    ) -> None:
        pass

    def require_callback(
        self: "BitbakeVisitorBase", file_path: str, require_target: SymbolInfo
    ) -> None:
        pass

    def export_callback(
        self: "BitbakeVisitorBase", file_path: str, export_target: SymbolInfo
    ) -> None:
        pass

    def unset_callback(
        self: "BitbakeVisitorBase", file_path: str, unset_target: SymbolInfo
    ) -> None:
        pass

    def unset_flag_callback(
        self: "BitbakeVisitorBase",
        file_path: str,
        unset_flag_target: SymbolInfo,
        unset_flag: SymbolInfo,
    ) -> None:
        pass

    # other events
    def warning_callback(
        self: "BitbakeVisitorBase", file_path: str, lineno: int, detail: str
    ) -> None:
        pass

    def error_callback(
        self: "BitbakeVisitorBase", file_path: str, lineno: int, detail: str
    ) -> None:
        pass
