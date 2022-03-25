# -----------------------------------------------------------------------------
# BSD 3-Clause License
#
# Copyright (c) 2020-2022, Science and Technology Facilities Council.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# -----------------------------------------------------------------------------
# Author R. W. Ford STFC Daresbury Lab
# -----------------------------------------------------------------------------

''' Performs py.test tests on the Call PSyIR node. '''

from __future__ import absolute_import
import pytest
from psyclone.psyir.nodes import (
    Call, Reference, ArrayReference, Schedule, Literal)
from psyclone.psyir.nodes.node import colored
from psyclone.psyir.symbols import ArrayType, INTEGER_TYPE, DataSymbol, \
    RoutineSymbol, NoType
from psyclone.errors import GenerationError


class SpecialCall(Call):
    '''Test Class specialising the Call class'''


def test_call_init():
    '''Test that a Call can be created as expected. Also test the routine
    property.

    '''
    # routine argument
    routine = RoutineSymbol("jo", NoType())
    call = Call(routine)
    assert call._routine is routine
    assert call.routine is call._routine
    assert call.parent is None
    assert call.children == []

    # optional parent argument
    parent = Schedule()
    call = Call(routine, parent=parent)
    assert call.routine is routine
    assert call.parent is parent
    assert call.children == []


def test_call_init_error():
    '''Test that the appropriate exception is raised if the routine
    argument is not a RoutineSymbol.

    '''
    with pytest.raises(TypeError) as info:
        _ = Call(None)
    assert ("Call routine argument should be a RoutineSymbol but found "
            "'NoneType'." in str(info.value))


@pytest.mark.parametrize("cls", [Call, SpecialCall])
def test_call_create(cls):
    '''Test that the create method creates a valid call with arguments,
    some of which are named. Also checks the routine and named_args
    properties.

    '''
    routine = RoutineSymbol("ellie", INTEGER_TYPE)
    array_type = ArrayType(INTEGER_TYPE, shape=[10, 20])
    arguments = [Reference(DataSymbol("arg1", INTEGER_TYPE)),
                 ArrayReference(DataSymbol("arg2", array_type))]
    call = cls.create(routine, [arguments[0], ("name", arguments[1])])
    # pylint: disable=unidiomatic-typecheck
    assert type(call) is cls
    assert call.routine is routine
    assert call.named_args == [None, "name"]
    for idx, child, in enumerate(call.children):
        assert child is arguments[idx]
        assert child.parent is call


def test_call_create_error1():
    '''Test that the appropriate exception is raised if the routine
    argument to the create method is not a RoutineSymbol.

    '''
    with pytest.raises(GenerationError) as info:
        _ = Call.create(None, [])
    assert ("Call create routine argument should be a RoutineSymbol but "
            "found 'NoneType'." in str(info.value))


def test_call_create_error2():
    '''Test that the appropriate exception is raised if the arguments
    argument to the create method is not a list'''
    routine = RoutineSymbol("isaac", NoType())
    with pytest.raises(GenerationError) as info:
        _ = Call.create(routine, None)
    assert ("Call create arguments argument should be a list but found "
            "'NoneType'." in str(info.value))


def test_call_create_error3():
    '''Test that the appropriate exception is raised if an entry in the
    arguments argument to the create method is is a tuple that does
    not have two elements.'''
    routine = RoutineSymbol("isaac", NoType())
    with pytest.raises(GenerationError) as info:
        _ = Call.create(routine, [(1, 2, 3)])
    assert ("If a child of the children argument in create method of Call "
            "class is a tuple, it's length should be 2, but found 3."
            in str(info.value))


def test_call_create_error4():
    '''Test that the appropriate exception is raised if an entry in the
    arguments argument to the create method is is a tuple with two
    elements and the first element is not a string.'''
    routine = RoutineSymbol("isaac", NoType())
    with pytest.raises(GenerationError) as info:
        _ = Call.create(routine, [(1, 2)])
    assert ("If a child of the children argument in create method of Call "
            "class is a tuple, its first argument should be a str, but "
            "found int." in str(info.value))


def test_call_create_error5():
    '''Test that the appropriate exception is raised if one or more of the
    arguments argument list entries to the create method is not a
    DataNode.

    '''
    routine = RoutineSymbol("roo", INTEGER_TYPE)
    with pytest.raises(GenerationError) as info:
        _ = Call.create(
            routine, [Reference(DataSymbol(
                "arg1", INTEGER_TYPE)), ("name", None)])
    assert ("Item 'NoneType' can't be child 1 of 'Call'. The valid format "
            "is: '[DataNode]*'." in str(info.value))


def test_call_appendnamedarg():
    '''Test the append_named_arg method in the Call class. Check
    it raises the expected exceptions if arguments are invalid and
    that it works as expected when the input is valid.

    '''
    op1 = Literal("1", INTEGER_TYPE)
    op2 = Literal("1", INTEGER_TYPE)
    call = Call.create(RoutineSymbol("hello"), [])
    # name arg wrong type
    with pytest.raises(TypeError) as info:
        call.append_named_arg(1, op1)
    assert ("The 'name' argument in 'append_named_arg' in the 'Call' "
            "node should be a string or None, but found int."
            in str(info.value))
    call.append_named_arg("name1", op1)
    # name arg already used
    with pytest.raises(ValueError) as info:
        call.append_named_arg("name1", op2)
    assert ("The value of the name argument (name1) in 'append_named_arg' in "
            "the 'Call' node is already used for a named argument."
            in str(info.value))
    # ok
    call.append_named_arg("name2", op2)
    assert call.children == [op1, op2]
    assert call.named_args == ["name1", "name2"]


def test_call_insertnamedarg():
    '''Test the insert_named_arg method in the Call class. Check
    it raises the expected exceptions if arguments are invalid and
    that it works as expected when the input is valid.

    '''
    op1 = Literal("1", INTEGER_TYPE)
    op2 = Literal("1", INTEGER_TYPE)
    call = Call.create(RoutineSymbol("hello"), [])
    # name arg wrong type
    with pytest.raises(TypeError) as info:
        call.insert_named_arg(1, op1, 0)
    assert ("The 'name' argument in 'insert_named_arg' in the 'Call' "
            "node should be a string or None, but found int."
            in str(info.value))
    call.insert_named_arg("name1", op1, 0)
    # name arg already used
    with pytest.raises(ValueError) as info:
        call.insert_named_arg("name1", op2, 0)
    assert ("The value of the name argument (name1) in 'insert_named_arg' in "
            "the 'Call' node is already used for a named argument."
            in str(info.value))
    # invalid index type
    with pytest.raises(ValueError) as info:
        call.insert_named_arg("name1", op2, "hello")
    assert ("The value of the name argument (name1) in 'insert_named_arg' in "
            "the 'Call' node is already used for a named argument."
            in str(info.value))
    # ok
    assert call.children == [op1]
    assert call.named_args == ["name1"]
    call.insert_named_arg("name2", op2, 0)
    assert call.children == [op2, op1]
    assert call.named_args == ["name2", "name1"]


def test_operation_replacenamedarg():
    '''Test the replace_named_arg method in the Call class. Check
    it raises the expected exceptions if arguments are invalid and
    that it works as expected when the input is valid.

    '''
    op1 = Literal("1", INTEGER_TYPE)
    op2 = Literal("1", INTEGER_TYPE)
    op3 = Literal("1", INTEGER_TYPE)
    call = Call.create(RoutineSymbol("hello"),
                       [("name1", op1), ("name2", op2)])

    # name arg wrong type
    with pytest.raises(TypeError) as info:
        call.replace_named_arg(1, op3)
    assert ("The 'name' argument in 'replace_named_arg' in the 'Call' "
            "node should be a string or None, but found int."
            in str(info.value))
    # name arg is not found
    with pytest.raises(ValueError) as info:
        call.replace_named_arg("new_name", op3)
    assert ("The value of the existing_name argument (new_name) in "
            "'insert_named_arg' in the 'Call' node is not found in the "
            "existing arguments." in str(info.value))
    # ok
    assert call.children == [op1, op2]
    assert call.named_args == ["name1", "name2"]
    call.replace_named_arg("name1", op3)
    assert call.children == [op3, op2]
    assert call.named_args == ["name1", "name2"]


def test_call_removearg():
    '''Test the named_args property makes things consistent if a child
    argument is removed. This is used transparently by the class to
    keep things consistent.

    '''
    op1 = Literal("1", INTEGER_TYPE)
    op2 = Literal("1", INTEGER_TYPE)
    call = Call.create(RoutineSymbol("name"), [("name1", op1), ("name2", op2)])
    assert len(call.children) == 2
    assert len(call._named_args) == 2
    assert call.named_args == ["name1", "name2"]
    call.children.pop(0)
    assert len(call.children) == 1
    assert len(call._named_args) == 2
    # named_args property makes _named_args list consistent.
    assert call.named_args == ["name2"]
    assert len(call._named_args) == 1


def test_call_addarg():
    '''Test the named_args property makes things consistent if a child
    argument is added. This is used transparently by the class to
    keep things consistent.

    '''
    op1 = Literal("1", INTEGER_TYPE)
    op2 = Literal("1", INTEGER_TYPE)
    op3 = Literal("1", INTEGER_TYPE)
    call = Call.create(RoutineSymbol("name"), [("name1", op1), ("name2", op2)])
    assert len(call.children) == 2
    assert len(call._named_args) == 2
    assert call.named_args == ["name1", "name2"]
    call.children.append(op3)
    assert len(call.children) == 3
    assert len(call._named_args) == 2
    # named_args property makes _named_args list consistent.
    assert call.named_args == ["name1", "name2", None]
    assert len(call._named_args) == 3


def test_call_replacearg():
    '''Test the named_args property makes things consistent if a child
    argument is replaced. This is used transparently by the class to
    keep things consistent.

    '''
    op1 = Literal("1", INTEGER_TYPE)
    op2 = Literal("1", INTEGER_TYPE)
    op3 = Literal("1", INTEGER_TYPE)
    call = Call.create(RoutineSymbol("name"), [("name1", op1), ("name2", op2)])
    assert len(call.children) == 2
    assert len(call._named_args) == 2
    assert call.named_args == ["name1", "name2"]
    call.children[0] = op3
    assert len(call.children) == 2
    assert len(call._named_args) == 2
    # named_args property makes _named_args list consistent.
    assert call.named_args == [None, "name2"]
    assert len(call._named_args) == 2


def test_call_reorderarg():
    '''Test the named_args property makes things consistent if a child
    argument is replaced. This is used transparently by the class to
    keep things consistent.

    '''
    op1 = Literal("1", INTEGER_TYPE)
    op2 = Literal("1", INTEGER_TYPE)
    op3 = Literal("1", INTEGER_TYPE)
    call = Call.create(RoutineSymbol("name"), [("name1", op1), ("name2", op2)])
    assert len(call.children) == 2
    assert len(call._named_args) == 2
    assert call.named_args == ["name1", "name2"]
    call.children[0] = op3
    assert len(call.children) == 2
    assert len(call._named_args) == 2
    # named_args property makes _named_args list consistent.
    assert call.named_args == [None, "name2"]
    assert len(call._named_args) == 2


def test_call_node_str():
    ''' Test that the node_str method behaves as expected '''
    routine = RoutineSymbol("isaac", NoType())
    call = Call(routine)
    colouredtext = colored("Call", Call._colour)
    assert call.node_str() == colouredtext+"[name='isaac']"


def test_call_str():
    ''' Test that the str method behaves as expected '''
    routine = RoutineSymbol("roo", NoType())
    call = Call(routine)
    assert str(call) == "Call[name='roo']"
