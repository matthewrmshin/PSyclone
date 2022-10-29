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
# Author R. W. Ford, STFC Daresbury Lab

'''Module containing the abstract CommonMetaArgMetadata class which
captures the metadata associated with an LFRic meta_arg
argument. Supports the creation, modification and Fortran output of
such an argument.

'''
from abc import ABC, abstractmethod

from psyclone.domain.lfric.kernel.common_arg_metadata import CommonArgMetadata
from psyclone.errors import InternalError


class CommonMetaArgMetadata(CommonArgMetadata, ABC):
    '''Abstract class to capture common LFRic kernel metadata.

    :param Optional[str] datatype: the datatype of this argument.
    :param Optional[str] access: the way the kernel accesses this \
        argument.

    '''
    # Dummy values to keep pylint happy for the class methods
    form_arg_index = 0
    vector_length_arg_index = 0
    datatype_arg_index = 1
    access_arg_index = 2
    function_space_arg_index = 3
    form = ""

    def __init__(self, datatype, access):
        self.datatype = datatype
        self.access = access

    @classmethod
    def check_first_arg(cls, fparser2_tree, name, vector=False):
        '''Check that the first metadata argument has the expected value.

        :param fparser2_tree: the metadata encoded in an fparser2_tree
        :type fparser2_tree: :py:class:`fparser.two.Fortran2003.Part_Ref` | \
            :py:class:`fparser.two.Fortran2003.Structure_Constructor`
        :param str name: the name used to describe this metadata.
        :param bool vector: whether this is vector metadata.

        :raises ValueError: if the first metadata argument has an \
            incorrect value.

        '''
        idx = cls.form_arg_index
        form = cls.get_arg(fparser2_tree, idx)
        word = "as"
        if vector:
            form = form.split("*")[0].strip()
            word = "in"
        if not form.lower() == cls.form.lower():
            raise ValueError(
                f"{name}s should have {cls.form} {word} their first metadata "
                f"argument, but found '{form}'.")

    @classmethod
    def check_remaining_args(cls, fparser2_tree, *metadata_args):
        '''Check that the remaining untested metadata arguments have the
        expected value. If they do not then re-raise the exception
        from the class constructor, adding in positional information
        and the metadata arguments to make it clearer where the
        exception occured.

        :param fparser2_tree: the metadata encoded in an fparser2_tree
        :type fparser2_tree: :py:class:`fparser.two.Fortran2003.Part_Ref` | \
            :py:class:`fparser.two.Fortran2003.Structure_Constructor`
        :param *metadata_args: the metadata arguments required to \
            create an instance of the class provided by the 'cls' \
            argument.
        :type *metadata_args: unwrapped dict

        :raises ValueError: if the metadata has an incorrect value.
        :raises InternalError: if an unrecognised exception message is found.

        '''
        try:
            _ = cls(*metadata_args)
        except ValueError as info:
            message = str(info)
            if "datatype descriptor" in message:
                index = cls.datatype_arg_index
            elif "access descriptor" in message:
                index = cls.access_arg_index
            elif "function space" in message:
                index = cls.function_space_arg_index
            elif "mesh_arg" in message:
                index = cls.mesh_arg_index
            elif "function_space_to" in message:
                index = cls.function_space_to_arg_index
            elif "function_space_from" in message:
                index = cls.function_space_from_arg_index
            else:
                raise InternalError(
                    f"Unexpected error message found '{message}'") from info
            raise ValueError(f"At argument index '{index}' for metadata "
                             f"'{str(fparser2_tree)}'. {message}") from info

    @classmethod
    def get_type_and_access(cls, fparser2_tree):
        '''Retrieves the datatype and access metadata values found within the
        supplied fparser2 tree.

        :param fparser2_tree: fparser2 tree capturing the required metadata.
        :type fparser2_tree: :py:class:`fparser.two.Fortran2003.Part_Ref`

        :returns: the datatype and access values extracted from the \
            fparser2 tree.
        :rtype: Tuple[str, str]

        '''
        datatype = CommonArgMetadata.get_arg(
            fparser2_tree, cls.datatype_arg_index)
        access = CommonArgMetadata.get_arg(fparser2_tree, cls.access_arg_index)
        return (datatype, access)

    @classmethod
    def get_type_access_and_fs(cls, fparser2_tree):
        '''Retrieves the datatype, access and function space metadata values
        found within the supplied fparser2 tree.

        :param fparser2_tree: fparser2 tree capturing the required metadata.
        :type fparser2_tree: :py:class:`fparser.two.Fortran2003.Part_Ref`

        :returns: the datatype, access and function space values \
            extracted from the fparser2 tree.
        :rtype: Tuple[str, str, str]

        '''
        datatype, access = cls.get_type_and_access(fparser2_tree)
        function_space = CommonArgMetadata.get_arg(
            fparser2_tree, cls.function_space_arg_index)
        return (datatype, access, function_space)

    @classmethod
    def get_and_check_vector_length(cls, fparser2_tree):
        '''Retrieves the vector length metadata value found within the
        supplied fparser2 tree.

        :param fparser2_tree: fparser2 tree capturing the required metadata.
        :type fparser2_tree: :py:class:`fparser.two.Fortran2003.Part_Ref`

        :returns: the vector length value extracted from the fparser2 tree.
        :rtype: str

        :raises TypeError: if the vector length metadata is not in the \
            expected form.

        '''
        vector_datatype = CommonArgMetadata.get_arg(
            fparser2_tree, cls.vector_length_arg_index)
        components = vector_datatype.split("*")
        if len(components) != 2:
            raise TypeError(
                f"The vector length metadata should be in the form "
                f"'form*vector_length' but found '{vector_datatype}'.")
        vector_length = components[1].strip()
        return vector_length

    @property
    def datatype(self):
        '''
        :returns: the datatype for this metadata argument.
        :rtype: str
        '''
        return self._datatype

    @staticmethod
    @abstractmethod
    def check_datatype(value):
        '''Check that value is a valid datatype.'''

    @datatype.setter
    def datatype(self, value):
        '''
        :param str value: set the datatype to the \
            specified value.
        '''
        self.check_datatype(value)
        self._datatype = value

    @staticmethod
    @abstractmethod
    def check_access(value):
        '''Check that value is a valid value for the access descriptor.'''

    @property
    def access(self):
        '''
        :returns: the access descriptor for this argument.
        :rtype: str
        '''
        return self._access

    @access.setter
    def access(self, value):
        '''
        :param str value: set the access descriptor to the \
            specified value.

        '''
        self.check_access(value)
        self._access = value
