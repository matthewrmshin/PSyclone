# -----------------------------------------------------------------------------
# BSD 3-Clause License
#
# Copyright (c) 2022, Science and Technology Facilities Council
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
# Author: A. R. Porter, STFC Daresbury Lab

''' pytest tests for the LFRic-specifc algorithm-generation functionality. '''

import pytest

from psyclone.domain.lfric.algorithm import alg_gen
from psyclone.psyir.nodes import Routine
from psyclone.psyir.symbols import ContainerSymbol


def test_create_alg_driver_wrong_arg_type():
    '''
    Test that _create_alg_driver() rejects arguments of the wrong type.
    '''
    with pytest.raises(TypeError) as err:
        alg_gen._create_alg_driver(5, None)
    assert ("Supplied program name must be a str but got 'int'" in
            str(err.value))
    with pytest.raises(TypeError) as err:
        alg_gen._create_alg_driver("my_test", "5")
    assert ("Supplied number of vertical levels must be an int but got "
            "'str'" in str(err.value))


def test_create_alg_driver(fortran_writer):
    ''' Test the correct operation of _create_alg_driver(). '''
    psyir = alg_gen._create_alg_driver("my_prog", 8)
    assert isinstance(psyir, Routine)
    assert psyir.symbol_table.lookup("r_def")
    # TODO #284 ideally we'd test that the generated code compiles.
    gen = fortran_writer(psyir)
    assert "program my_prog" in gen
    assert "uniform_extrusion_type(0.0_r_def, 100.0_r_def, 8)" in gen


def test_create_function_spaces_no_spaces(fortran_writer):
    ''' Check that a Routine is populated as expected, even when there
    are no actual function spaces. '''
    prog = Routine("my_test", is_program=True)
    prog.symbol_table.new_symbol("fs_continuity_mod",
                                 symbol_type=ContainerSymbol)
    alg_gen._create_function_spaces(prog, [])
    assert prog.symbol_table.lookup("element_order")
    assert prog.symbol_table.lookup("ndata_sz")
    gen = fortran_writer(prog)
    assert f"ndata_sz = {alg_gen.NDATA_SIZE}" in gen
