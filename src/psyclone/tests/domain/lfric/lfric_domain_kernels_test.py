# -----------------------------------------------------------------------------
# BSD 3-Clause License
#
# Copyright (c) 2020, Science and Technology Facilities Council.
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

''' This module contains pytest tests for LFRic kernels which operate on
    the 'domain'. '''

from __future__ import absolute_import
import pytest
from fparser import api as fpapi
from psyclone.configuration import Config
from psyclone.dynamo0p3 import DynKernMetadata
from psyclone.parse.utils import ParseError

TEST_API = "dynamo0.3"


@pytest.fixture(scope="module", autouse=True)
def setup():
    '''Make sure that all tests here use dynamo0.3 as API.'''
    Config.get().api = TEST_API


def test_domain_kernel():
    ''' Check that we can successfully parse metadata that specifies a
    kernel with operates_on = DOMAIN. '''
    ast = fpapi.parse('''
module testkern_domain_mod
  type, extends(kernel_type) :: testkern_domain_type
     type(arg_type), meta_args(5) =                   &
          (/ arg_type(gh_scalar, gh_real, gh_read),   &
             arg_type(gh_field, gh_inc, w1),          &
             arg_type(gh_field, gh_read, w2),         &
             arg_type(gh_field, gh_read, w3),         &
             arg_type(gh_scalar, gh_integer, gh_read) &
           /)
     integer :: operates_on = domain
   contains
     procedure, nopass :: code => testkern_domain_code
  end type testkern_domain_type
contains
  subroutine testkern_domain_code(a, b, c, d)
  end subroutine testkern_domain_code
end module testkern_domain_mod
''', ignore_comments=False)
    dkm = DynKernMetadata(ast, name="testkern_domain_type")
    assert dkm.iterates_over == "domain"


def test_invalid_arg_domain_kernel():
    ''' Check that we reject a domain kernel if its metadata specifies
    an operator argument. '''
    ast = fpapi.parse('''module testkern_domain_mod
  type, extends(kernel_type) :: testkern_domain_type
     type(arg_type), meta_args(4) =                   &
          (/ arg_type(gh_scalar, gh_real, gh_read),   &
             arg_type(gh_field, gh_inc, w1),          &
             arg_type(gh_field, gh_read, w2),         &
             arg_type(gh_operator, gh_read, w2, w2)   &
           /)
     integer :: operates_on = domain
   contains
     procedure, nopass :: code => testkern_domain_code
  end type testkern_domain_type
contains
  subroutine testkern_domain_code(a, b, c, d)
  end subroutine testkern_domain_code
end module testkern_domain_mod
''', ignore_comments=False)
    with pytest.raises(ParseError) as err:
        DynKernMetadata(ast, name="testkern_domain_type")
    assert ("'domain' is only permitted to accept scalar and field arguments "
            "but the metadata for kernel 'testkern_domain_type' includes an "
            "argument of type 'gh_operator'" in str(err.value))


def test_invalid_basis_domain_kernel():
    ''' Check that we reject a kernel with operates_on=domain if it requires
    basis functions. '''
    ast = fpapi.parse('''
module testkern_domain_mod
  type, extends(kernel_type) :: testkern_domain_type
     type(arg_type), meta_args(3) =                   &
          (/ arg_type(gh_scalar, gh_real, gh_read),   &
             arg_type(gh_field, gh_inc, w1),          &
             arg_type(gh_field, gh_read, w2)          &
           /)
     type(func_type), dimension(2) :: meta_funcs =  &
          (/ func_type(w1, gh_basis),               &
             func_type(w2, gh_diff_basis)           &
           /)
     integer :: operates_on = domain
     integer :: gh_shape = gh_quadrature_XYoZ
   contains
     procedure, nopass :: code => testkern_domain_code
  end type testkern_domain_type
contains
  subroutine testkern_domain_code(a, b, c, d)
  end subroutine testkern_domain_code
end module testkern_domain_mod
''')
    with pytest.raises(ParseError) as err:
        DynKernMetadata(ast, name="testkern_domain_type")
    assert ("'domain' cannot be passed basis/differential basis functions "
            "but the metadata for kernel 'testkern_domain_type' contains an "
            "entry for 'meta_funcs'" in str(err.value))


def test_invalid_mesh_props_domain_kernel():
    ''' Check that we reject a kernel with operates_on=domain if it requires
    properties of the mesh. '''
    ast = fpapi.parse('''
module testkern_domain_mod
  type, extends(kernel_type) :: testkern_domain_type
     type(arg_type), meta_args(2) =                   &
          (/ arg_type(gh_scalar, gh_real, gh_read),   &
             arg_type(gh_field, gh_inc, w1)           &
           /)
     type(mesh_data_type), dimension(1) :: meta_mesh = &
                        (/ mesh_data_type(adjacent_face) /)
     integer :: operates_on = domain
   contains
     procedure, nopass :: code => testkern_domain_code
  end type testkern_domain_type
contains
  subroutine testkern_domain_code(a, b, c, d)
  end subroutine testkern_domain_code
end module testkern_domain_mod
''')
    with pytest.raises(ParseError) as err:
        DynKernMetadata(ast, name="testkern_domain_type")
    assert ("'testkern_domain_type' operates on the domain but requests "
            "properties of the mesh ([" in str(err.value))
