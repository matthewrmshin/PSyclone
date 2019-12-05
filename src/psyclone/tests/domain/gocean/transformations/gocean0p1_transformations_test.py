# -------------------------------------------------------------------------
# (c) The copyright relating to this work is owned jointly by the Crown,
# Met Office and NERC 2015.
# However, it has been created with the help of the GungHo Consortium,
# whose members are identified at https://puma.nerc.ac.uk/trac/GungHo/wiki
# -------------------------------------------------------------------------
# Authors R. Ford and A. R. Porter, STFC Daresbury Lab

''' Contains tests for transformations on the GOcean 0.1 API '''

from __future__ import absolute_import
import pytest
from psyclone.configuration import Config
from psyclone.psyir.transformations import TransformationError
from psyclone.tests.utilities import get_invoke
from psyclone.transformations import LoopFuseTrans, GOceanLoopFuseTrans, \
    GOceanOMPParallelLoopTrans

API = "gocean0.1"


@pytest.fixture(scope="module", autouse=True)
def setup():
    '''Make sure that all tests here use gocean0.1 as API.'''
    Config.get().api = "gocean0.1"


def test_loop_fuse_with_not_a_loop():
    ''' Test that an appropriate error is raised by the LoopFuseTrans
    base class wen we attempt to fuse a loop with something that
    is not a loop '''
    _, invoke = get_invoke("openmp_fuse_test.f90", API, name="invoke_0")
    schedule = invoke.schedule
    # Use the bare LoopFuseTrans in order tests its error checking
    lftrans = LoopFuseTrans()
    ompf = GOceanOMPParallelLoopTrans()
    # Enclose the first loop within an OMP parallel do
    new_sched, _ = ompf.apply(schedule.children[0])
    # Attempt to (erroneously) fuse this OMP parallel do
    # with the next loop in the schedule
    with pytest.raises(TransformationError) as ex:
        schedule, _ = lftrans.apply(new_sched.children[0],
                                    new_sched.children[1])
    # Exercise the __str__ method of TransformationError
    assert "At least one of the nodes is not a loop." in str(ex.value)


def test_loop_fuse_on_non_siblings():
    ''' Test that an appropriate error is raised when we attempt to
    fuse two loops that do not share the same parent node in
    the schedule '''
    _, invoke = get_invoke("openmp_fuse_test.f90", API, name="invoke_0")
    schedule = invoke.schedule
    lftrans = LoopFuseTrans()

    # Attempt to fuse an outer loop with an inner loop
    with pytest.raises(TransformationError):
        _, _ = lftrans.apply(schedule.children[0],
                             schedule.children[1].
                             children[0])


def test_loop_fuse_non_adjacent_nodes():
    ''' Test that an appropriate error is raised when we attempt to
    fuse two loops that are not adjacent to one another in the
    schedule '''
    _, invoke = get_invoke("openmp_fuse_test.f90", API, name="invoke_0")
    schedule = invoke.schedule
    lftrans = LoopFuseTrans()

    # Attempt to fuse two loops that are not adjacent to one another
    # in the schedule
    with pytest.raises(TransformationError):
        _, _ = lftrans.apply(schedule.children[0],
                             schedule.children[2])


def test_gocean_loop_fuse_with_not_a_loop():
    ''' Test that an appropriate error is raised by the GOceanLoopFuseTrans
    class when we attempt to fuse a loop with something that
    is not a loop '''
    _, invoke = get_invoke("openmp_fuse_test.f90", API, name="invoke_0")
    schedule = invoke.schedule
    # Use the bare LoopFuseTrans in order tests its error checking
    lftrans = GOceanLoopFuseTrans()
    ompf = GOceanOMPParallelLoopTrans()
    # Enclose the first loop within an OMP parallel do
    new_sched, _ = ompf.apply(schedule.children[0])
    # Attempt to (erroneously) fuse this OMP parallel do
    # with the next loop in the schedule
    with pytest.raises(TransformationError):
        _, _ = lftrans.apply(new_sched.children[0],
                             new_sched.children[1])


def test_openmp_loop_fuse_trans():
    ''' test of the OpenMP transformation of a fused loop '''
    psy, invoke = get_invoke("openmp_fuse_test.f90", API, name="invoke_0")
    schedule = invoke.schedule
    lftrans = GOceanLoopFuseTrans()
    ompf = GOceanOMPParallelLoopTrans()

    # fuse all outer loops
    lf_schedule, _ = lftrans.apply(schedule.children[0],
                                   schedule.children[1])
    schedule, _ = lftrans.apply(lf_schedule.children[0],
                                lf_schedule.children[1])
    # fuse all inner loops
    lf_schedule, _ = lftrans.apply(schedule.children[0].loop_body[0],
                                   schedule.children[0].loop_body[1])
    schedule, _ = lftrans.apply(lf_schedule.children[0].loop_body[0],
                                lf_schedule.children[0].loop_body[1])

    # Add an OpenMP directive around the fused loop
    lf_schedule, _ = ompf.apply(schedule.children[0])

    # Replace the original loop schedule with the transformed one
    psy.invokes.get('invoke_0').schedule = lf_schedule

    # Store the results of applying this code transformation as
    # a string
    gen = str(psy.gen)

    # Iterate over the lines of generated code
    for idx, line in enumerate(gen.split('\n')):
        if '!$omp parallel do' in line:
            omp_do_idx = idx
        if 'DO j=' in line:
            outer_do_idx = idx
        if 'DO i=' in line:
            inner_do_idx = idx

    # The OpenMP 'parallel do' directive must occur immediately before
    # the DO loop itself
    assert outer_do_idx-omp_do_idx == 1 and\
        outer_do_idx-inner_do_idx == -1


def test_loop_fuse_different_spaces():
    ''' Test that we raise an error if we attempt to fuse loops that are
    over different grid-point types '''
    _, invoke = get_invoke("fuse_different_spaces_test.f90", API,
                           name="invoke_0")
    schedule = invoke.schedule
    lftrans = GOceanLoopFuseTrans()
    with pytest.raises(TransformationError):
        _, _ = lftrans.apply(schedule.children[0],
                             schedule.children[1])


def test_openmp_loop_trans():
    ''' test of the OpenMP transformation of an all-points loop '''
    psy, invoke = get_invoke("openmp_fuse_test.f90", API, name="invoke_0")
    schedule = invoke.schedule
    ompf = GOceanOMPParallelLoopTrans()

    omp1_schedule, _ = ompf.apply(schedule.children[0])

    # Replace the original loop schedule with the transformed one
    psy.invokes.get('invoke_0').schedule = omp1_schedule

    # Store the results of applying this code transformation as
    # a string
    gen = str(psy.gen)

    omp_do_idx = -1
    # Iterate over the lines of generated code
    for idx, line in enumerate(gen.split('\n')):
        if '!$omp parallel do' in line:
            omp_do_idx = idx
        if 'DO j=' in line:
            outer_do_idx = idx
        if 'DO i=' in line:
            inner_do_idx = idx
            if omp_do_idx > -1:
                break

    # The OpenMP 'parallel do' directive must occur immediately before
    # the DO loop itself
    assert outer_do_idx-omp_do_idx == 1 and\
        inner_do_idx-outer_do_idx == 1
