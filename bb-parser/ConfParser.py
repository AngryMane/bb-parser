"""
   class for handling configuration data files
"""

# Copyright (C) 2003, 2004  Chris Larson
# Copyright (C) 2003, 2004  Phil Blundell
#
# SPDX-License-Identifier: GPL-2.0-only
#

import re
from symtable import Symbol
from typing import Optional
from webbrowser import Opera
from BitbakeVisitor import BitbakeVisitorBase, SymbolInfo, VariableInfo, OperatorInfo, Position

class ConfParser:

    __config_regexp__  = re.compile( r"""
        ^
        (?P<exp>export\s+)?
        (?P<var>[a-zA-Z0-9\-_+.${}/~:]+?)
        (\[(?P<flag>[a-zA-Z0-9\-_+.]+)\])?

        \s* (
            (?P<colon>:=) |
            (?P<lazyques>\?\?=) |
            (?P<ques>\?=) |
            (?P<append>\+=) |
            (?P<prepend>=\+) |
            (?P<predot>=\.) |
            (?P<postdot>\.=) |
            =
        ) \s*

        (?!'[^']*'[^']*'$)
        (?!\"[^\"]*\"[^\"]*\"$)
        (?P<apo>['\"])
        (?P<value>.*)
        (?P=apo)
        $
        """, re.X)
    __include_regexp__ = re.compile( r"include\s+(.+)" )
    __require_regexp__ = re.compile( r"require\s+(.+)" )
    __export_regexp__ = re.compile( r"export\s+([a-zA-Z0-9\-_+.${}/~]+)$" )
    __unset_regexp__ = re.compile( r"unset\s+([a-zA-Z0-9\-_+.${}/~]+)$" )
    __unset_flag_regexp__ = re.compile( r"unset\s+([a-zA-Z0-9\-_+.${}/~]+)\[([a-zA-Z0-9\-_+.]+)\]$" )

    def __init__(self: "ConfParser", visitor: BitbakeVisitorBase) -> None:
        self.__visitor: BitbakeVisitorBase = visitor

    def __configure_event(self: "ConfParser", lineno: int, line: str, matched: Optional[re.Match]):
        symbol_name: str = matched.group("var")
        matched_var_span: tuple[int, int] = matched.span("var")
        is_append: bool = True if matched.group("append") else False
        is_prepend: bool = True if matched.group("prepend") else False
        variable_info: VariableInfo = VariableInfo(symbol_name, Position(lineno, matched_var_span[0]), Position(lineno, matched_var_span[1]), is_append, is_prepend)

        flag_name: Optional[str] = matched.group("flag")
        matched_flag_span: tuple[int, int] = matched.span("flag")
        flag: Optional[SymbolInfo] = SymbolInfo(flag_name, Position(lineno, matched_flag_span[0]), Position(lineno, matched_flag_span[1])) if matched.group("flag") else None

        is_immediate_expand: bool = True if matched.group("colon") else False
        is_weak: bool = True if matched.group("ques") else False
        is_weak_weak: bool = True if matched.group("lazyques") else False
        is_predot: bool = True if matched.group("predot") else False
        is_postdot: bool = True if matched.group("postdot") else False
        operator: OperatorInfo = OperatorInfo(is_immediate_expand, is_weak, is_weak_weak, is_predot, is_postdot)

        value_str: str = matched.group("value")
        matched_value_span: tuple[int, int] = matched.span("value")
        value_info: SymbolInfo = SymbolInfo(value_str, Position(lineno, matched_value_span[0]), Position(lineno, matched_value_span[1]))

        is_export: bool = True if matched.group("exp") else False
        self.__visitor.config_callback(is_export, variable_info, flag, operator, value_info)

    def parse_line(self: "ConfParser", lineno, s):
        m = self.__config_regexp__.match(s)
        if m:
            self.__configure_event(lineno, s, m)
            return

        m = self.__include_regexp__.match(s)
        if m:
            include_target: SymbolInfo = SymbolInfo(m.group(1), Position(lineno, m.span(1)[0]), Position(lineno, m.span(1)[1]))
            self.__visitor.include_callback(include_target)
            return

        m = self.__require_regexp__.match(s)
        if m:
            require_target: SymbolInfo = SymbolInfo(m.group(1), Position(lineno, m.span(1)[0]), Position(lineno, m.span(1)[1]))
            self.__visitor.require_callback(require_target)
            return

        m = self.__export_regexp__.match(s)
        if m:
            export_target: SymbolInfo = SymbolInfo(m.group(1), Position(lineno, m.span(1)[0]), Position(lineno, m.span(1)[1]))
            self.__visitor.export_callback(export_target)
            return

        m = self.__unset_regexp__.match(s)
        if m:
            unset_target: SymbolInfo = SymbolInfo(m.group(1), Position(lineno, m.span(1)[0]), Position(lineno, m.span(1)[1]))
            self.__visitor.unset_callback(unset_target)
            return

        m = self.__unset_flag_regexp__.match(s)
        if m:
            unset_target: SymbolInfo = SymbolInfo(m.group(1), Position(lineno, m.span(1)[0]), Position(lineno, m.span(1)[1]))
            unset_flag: SymbolInfo = SymbolInfo(m.group(2), Position(lineno, m.span(2)[0]), Position(lineno, m.span(2)[1]))
            self.__visitor.unset_flag_callback(unset_target, unset_flag)
            return

        # TODO: add error log
        #raise ParseError("unparsed line: '%s'" % s, fn, lineno);

