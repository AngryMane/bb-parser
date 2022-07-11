"""
   class for handling .bb files
"""


#  Copyright (C) 2003, 2004  Chris Larson
#  Copyright (C) 2003, 2004  Phil Blundell
#
# SPDX-License-Identifier: GPL-2.0-only
#

import re
from enum import Enum
from collections import namedtuple
from typing import List, Optional

from BitbakeVisitor import BitbakeVisitorBase, FunctionBody, FunctionHeader, Position, SymbolInfo
from ConfParser import ConfParser

# callback type definitions
FunctionInfo = namedtuple("FunctionInfo", ["name", "lineno", "span", "is_python", "is_fakeroot", "header_raw_text"])

# TODO:
# This class has complex state machine based on feeded lines.
# Therefore, I think this class should be implemented by function-table design.

class BitbakeParser:

    __func_start_regexp__    = re.compile(r"(((?P<py>python(?=(\s|\()))|(?P<fr>fakeroot(?=\s)))\s*)*(?P<func>[\w\.\-\+\{\}\$:]+)?\s*\(\s*\)\s*{$" )
    __inherit_regexp__       = re.compile(r"inherit\s+(.+)" )
    __export_func_regexp__   = re.compile(r"EXPORT_FUNCTIONS\s+(.+)" )
    __addtask_regexp__       = re.compile(r"addtask\s+(?P<func>\w+)\s*((before\s*(?P<before>((.*(?=after))|(.*))))|(after\s*(?P<after>((.*(?=before))|(.*)))))*")
    __deltask_regexp__       = re.compile(r"deltask\s+(.+)")
    __addhandler_regexp__    = re.compile(r"addhandler\s+(.+)" )
    __def_regexp__           = re.compile(r"def\s+(\w+).*:" )
    __python_func_regexp__   = re.compile(r"(\s+.*)|(^$)|(^#)" )
    __python_tab_regexp__    = re.compile(r" *\t")

    def __init__(self: "BitbakeParser", visitor: BitbakeVisitorBase) -> None:
        self.__initialize()
        self.__visitor: BitbakeVisitorBase = visitor
        self.__conf_parser: ConfParser = ConfParser(visitor)

    def parse(self: "BitbakeParser", absolute_file_path: str) -> List[str]:
        conf_contents: List[str] = []

        self.__initialize()
        with open(absolute_file_path, 'r') as f:
            lineno = 0
            while True:
                lineno = lineno + 1
                s = f.readline()
                if not s: break
                s = s.rstrip()
                ret: Optional[str] = self.__feeder(lineno, s)
                conf_contents.append(ret or "")
        if self.__inpython__:
            self.__feeder(lineno, "", eof=True)
        self.__teardown()

        return conf_contents

    def __initialize(self: "BitbakeParser"):
        self.__teardown()

    def __teardown(self: "BitbakeParser"):
        self.__infunc__: Optional[FunctionInfo] = None
        self.__inpython__: Optional[FunctionInfo]  = None
        self.__body__: List   = []
        self.__classname__: str = ""
        self.__residue__: List = []

    def __infunc_event(self: "BitbakeParser", lineno: int, line: str):
        if line == '}':
            self.__body__.append('')
            body = [self.__infunc__.header_raw_text]
            body.extend(self.__body__)
            body.append(line)

            header: FunctionHeader = FunctionHeader(
                self.__infunc__.name, 
                self.__infunc__.header_raw_text, 
                Position(self.__infunc__.lineno, self.__infunc__.span[0]),
                Position(self.__infunc__.lineno, self.__infunc__.span[1]),
                self.__infunc__.is_python, 
                self.__infunc__.is_fakeroot)
            function_body: FunctionBody = FunctionBody(body, Position(self.__infunc__.lineno, 0), Position(lineno, 1))
            self.__visitor.function_callback(header, function_body)

            self.__infunc__ = None
            self.__body__ = []
        else:
            self.__body__.append(line)

    def __inpython_func_event(self: "BitbakeParser", lineno: int, line: str):
        self.__body__.append(line)

    def __python_func_event(self: "BitbakeParser", lineno: int, line: str):
        header: FunctionHeader = FunctionHeader(
            self.__inpython__.name, 
            self.__inpython__.header_raw_text, 
            Position(self.__inpython__.lineno, self.__inpython__.span[0]),
            Position(self.__inpython__.lineno, self.__inpython__.span[1]),
            True, 
            False)
        function_body: FunctionBody = FunctionBody(self.__body__, Position(self.__inpython__.lineno, self.__inpython__.span[0]), Position(lineno - 1, 0))
        self.__visitor.python_function_callback(header, function_body)
        self.__body__ = []
        self.__inpython__ = None

    def __funcstart_event(self: "BitbakeParser", lineno: int, line: str, matched: Optional[re.Match]):
        self.__infunc__ = FunctionInfo(
            matched.group("func") or "__anonymous", 
            lineno, 
            matched.span("func"),
            matched.group("py") is not None, 
            matched.group("fr") is not None, 
            line)

    def __def_event(self: "BitbakeParser", lineno: int, line: str, matched: Optional[re.Match]):
        self.__body__.append(line)
        self.__inpython__ = FunctionInfo(matched.group(1), lineno, matched.span(), True, False, line)

    def __export_func_event(self: "BitbakeParser", lineno: int, line: str, matched: Optional[re.Match]):
        self.__visitor.export_function_callback(matched.group(1), Position(lineno, matched.span(1)[0]), Position(lineno, matched.span(1)[1]))

    def __addtask_event(self: "BitbakeParser", lineno: int, line: str, matched: Optional[re.Match]):
        if len(matched.group().split()) == 2:
            m2 = re.match(r"addtask\s+(?P<func>\w+)(?P<ignores>.*)", line)
            if m2 and m2.group('ignores'):
                # TODO: add error log
                #logger.warning('addtask ignored: "%s"' % m2.group('ignores'))
                pass

        taskexpression = line.split()
        for word in ('before', 'after'):
            if taskexpression.count(word) > 1:
                # TODO: add error log
                #logger.warning("addtask contained multiple '%s' keywords, only one is supported" % word)
                pass

        for te in taskexpression:
            # TODO: check keyword
            #if any( ( "%s_" % keyword ) in te for keyword in bb.data_smart.__setvar_keyword__ ):
                #raise ParseError("Task name '%s' contains a keyword which is not recommended/supported.\nPlease rename the task not to include the keyword.\n%s" % (te, ("\n".join(map(str, bb.data_smart.__setvar_keyword__)))), fn)
            pass

        added_task: SymbolInfo = SymbolInfo(matched.group(1), Position(lineno, matched.span(1)[0]), Position(lineno, matched.span(1)[1]))

        before: List[SymbolInfo] = []
        if matched.group("before"):
            for tsk in matched.group("before").split():
                start_pos = matched.span("before")[0] + matched.group("before").find(tsk)
                end_pos = start_pos + len(tsk)
                before.append(SymbolInfo(tsk, Position(lineno, start_pos), Position(lineno, end_pos)))

        after: List[SymbolInfo] = []
        if matched.group("after"):
            for tsk in matched.group("after").split():
                start_pos = matched.span("after")[0] + matched.group("after").find(tsk)
                end_pos = start_pos + len(tsk)
                after.append(SymbolInfo(tsk, Position(lineno, start_pos), Position(lineno, end_pos)))

        self.__visitor.add_task_callback(added_task, before, after)

    def __del_task_event(self: "BitbakeParser", lineno: int, line: str, matched: Optional[re.Match]):
        deleted_task: SymbolInfo = SymbolInfo(matched.group(1), Position(lineno, matched.span(1)[0]), Position(lineno, matched.span(1)[1]))
        self.__visitor.delete_task_callback(deleted_task)

    def __add_handler_event(self: "BitbakeParser", lineno: int, line: str, matched: Optional[re.Match]):
        handler_task: SymbolInfo = SymbolInfo(matched.group(1), Position(lineno, matched.span(1)[0]), Position(lineno, matched.span(1)[1]))
        self.__visitor.add_handler_callback(handler_task)

    def __inherit_event(self: "BitbakeParser", lineno: int, line: str, matched: Optional[re.Match]):
        inherit_target_names: List[SymbolInfo] = []
        for target in matched.group(1).split():
            start_pos = matched.span(1)[0] + matched.group(1).find(target)
            end_pos = start_pos + len(target)
            inherit_target_names.append(SymbolInfo(target, Position(lineno, start_pos), Position(lineno, end_pos)))
        self.__visitor.inherit_callback(inherit_target_names)

    def __feeder(self: "BitbakeParser", lineno, s, eof=False) -> Optional[str]:
        if self.__inpython__ or (self.__infunc__ and ('__anonymous' == self.__infunc__.name or self.__infunc__.is_python)):
            tab = self.__python_tab_regexp__.match(s)
            if tab:
                # TODO: add error log
                #bb.warn('python should use 4 spaces indentation, but found tabs in %s, line %s' % (root, lineno))
                pass

        if self.__infunc__:
            self.__infunc_event(lineno, s)
            return

        if self.__inpython__:
            m = self.__python_func_regexp__.match(s)
            if m and not eof:
                self.__inpython_func_event(lineno, s)
                return
            else:
                self.__python_func_event(lineno, s)
                if eof:
                    return

        if s and s[0] == '#':
            if len(self.__residue__) != 0 and self.__residue__[0][0] != "#":
                # TODO: add error log
                #bb.fatal("There is a comment on line %s of file %s (%s) which is in the middle of a multiline expression.\nBitbake used to ignore these but no longer does so, please fix your metadata as errors are likely as a result of this change." % (lineno, fn, s))
                pass

        if len(self.__residue__) != 0 and self.__residue__[0][0] == "#" and (not s or s[0] != "#"):
            # TODO: add error log
            # bb.fatal("There is a confusing multiline, partially commented expression on line %s of file %s (%s).\nPlease clarify whether this is all a comment or should be parsed." % (lineno, fn, s))
            pass

        if s and s[-1] == '\\':
            self.__residue__.append(s[:-1])
            return

        s = "".join(self.__residue__) + s
        self.__residue__ = []

        # Skip empty lines
        if s == '':
            return   

        # Skip comments
        if s[0] == '#':
            return

        m = self.__func_start_regexp__.match(s)
        if m:
            self.__funcstart_event(lineno, s, m)
            return

        m = self.__def_regexp__.match(s)
        if m:
            self.__def_event(lineno, s, m)
            return

        m = self.__export_func_regexp__.match(s)
        if m:
            self.__export_func_event(lineno, s, m)
            return

        m = self.__addtask_regexp__.match(s)
        if m:
            self.__addtask_event(lineno, s, m)
            return

        m = self.__deltask_regexp__.match(s)
        if m:
            self.__del_task_event(lineno, s, m)
            return

        m = self.__addhandler_regexp__.match(s)
        if m:
            self.__add_handler_event(lineno, s, m)
            return

        m = self.__inherit_regexp__.match(s)
        if m:
            self.__inherit_event(lineno, s, m)
            return

        self.__conf_parser.parse_line(lineno, s)