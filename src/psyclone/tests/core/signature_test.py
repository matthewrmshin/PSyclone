# -----------------------------------------------------------------------------
# BSD 3-Clause License
#
# Copyright (c) 2021, Science and Technology Facilities Council.
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
# Author: Joerg Henrichs, Bureau of Meteorology

'''This module tests the Signature class.'''

from __future__ import absolute_import
import pytest

from psyclone.core import Signature
from psyclone.errors import InternalError


def test_signature():
    '''Test the Signature class.
    '''

    assert str(Signature("a")) == "a"
    assert str(Signature(("a",))) == "a"
    assert str(Signature(("a", "b", "c"))) == "a%b%c"
    assert repr(Signature("a")) == "Signature(a)"
    assert repr(Signature(("a",))) == "Signature(a)"
    assert repr(Signature(("a", "b", "c"))) == "Signature(a%b%c)"
    assert Signature("a") != "a"


def test_signature_errors():
    '''Tests error handling of Signature class.
    '''
    with pytest.raises(InternalError) as err:
        _ = Signature(1)

    assert "Got unexpected type 'int' in Signature" in str(err.value)


def test_signature_dict():
    '''Test that Signature instances work as expected as dictionary keys.
    '''
    sig1 = Signature("a")
    sig2 = Signature("a")
    assert sig1 is not sig2

    # Make sure that different instances representing the same signature
    # will have the same hash:
    test_dict = {}
    test_dict[sig1] = "a"
    assert test_dict[sig2] == "a"

    sig3 = Signature(("a", "b"))
    test_dict[sig3] = "ab"
    sig4 = Signature(("a", "c"))
    test_dict[sig4] = "ac"

    assert len(test_dict) == 3


def test_concatenate_signature():
    '''Tests that signature can be concatenated.'''
    sig_b = Signature("b")
    sig_a_b = Signature("a", sig_b)
    assert str(sig_a_b) == "a%b"
    sig_b_a_b = Signature(sig_b, sig_a_b)
    assert str(sig_b_a_b) == "b%a%b"
    sig_c_d_b_a_b = Signature(("c", "d"), sig_b_a_b)
    assert str(sig_c_d_b_a_b) == "c%d%b%a%b"


def test_var_name():
    '''Test that the variable name is returned as expected.'''
    sig_a = Signature("a")
    assert sig_a.var_name == "a"
    sig_a_b = Signature(sig_a, Signature("b"))
    assert str(sig_a_b) == "a%b"
    assert sig_a_b.var_name == "a"


def test_signature_sort():
    '''Test that signatures can be sorted.'''

    sig_list = [Signature("c"), Signature("a"), Signature("b"),
                Signature(("b", "a")),
                Signature(("a", "c")), Signature(("a", "b"))]

    assert str(sig_list) == "[Signature(c), Signature(a), Signature(b), " \
                            "Signature(b%a), Signature(a%c), Signature(a%b)]"

    sig_list.sort()
    assert str(sig_list) == "[Signature(a), Signature(a%b), Signature(a%c), " \
                            "Signature(b), Signature(b%a), Signature(c)]"


def test_signature_comparison():
    ''' Test that two Signatures can be compared for equality and not
    equality.
    '''
    assert Signature(("a", "b")) == Signature(("a", "b"))
    # pylint: disable=unneeded-not
    assert not Signature(("a", "b")) != Signature(("a", "b"))
    assert Signature(("a", "b")) != Signature(("a", "c"))
    assert not Signature(("a", "b")) == Signature(("a", "c"))
    assert Signature(("a", "c")) >= Signature(("a", "b"))
    assert Signature(("a", "c")) > Signature(("a", "b"))
    assert Signature(("a", "b")) <= Signature(("a", "c"))
    assert Signature(("a", "b")) < Signature(("a", "c"))

    # Comparison with other types should work for == and !=:
    assert not Signature(("a", "b")) == 2
    assert Signature(("a", "b")) != 2

    # Error cases: comparison of signature with other type.
    # We don't check for the other type name in the message,
    # since this varies between python 2 and 3.
    with pytest.raises(TypeError) as err:
        _ = Signature(("a", "b")) < 1

    assert "'<' not supported between instances of 'Signature' and" \
        in str(err.value)

    with pytest.raises(TypeError) as err:
        _ = Signature(("a", "b")) <= 1

    assert "'<=' not supported between instances of 'Signature' and" \
        in str(err.value)

    with pytest.raises(TypeError) as err:
        _ = Signature(("a", "b")) > 1

    assert "'>' not supported between instances of 'Signature' and" \
        in str(err.value)

    with pytest.raises(TypeError) as err:
        _ = Signature(("a", "b")) >= 1

    assert "'>=' not supported between instances of 'Signature' and" \
        in str(err.value)
