
module profiler_mod
  type :: ProfilerData
     character(:), allocatable :: module_name
     character(:), allocatable :: region_name
  end type ProfilerData

  logical :: has_been_initialised = .false.

contains
  ! ---------------------------------------------------------------------------
  ! An optional initialisation subroutine. It is not called directly from
  ! any PSycloen created code, but for most existing profilint libraries a
  ! requirement. In this dummy library it is called once from ProfileStart.
  !
  subroutine ProfileInit()
    implicit none
    print *,"ProfileInit called"
    has_been_initialised = .true.
  end subroutine ProfileInit

  ! ---------------------------------------------------------------------------
  ! Starts a profiling area. The module and region name can be used to create
  ! a unique name for each region.
  ! Parameters: 
  ! module_name:  Name of the module in which the region is
  ! region_name:  Name of the region (could be name of an invoke, or
  !               subroutine name).
  ! profile_data: Persistent data used by the profiling library.
  subroutine ProfileStart(module_name, region_name, profiler_data)
    implicit none

    character*(*) :: module_name, region_name
    type(ProfilerData) :: profiler_data

    if ( .not. has_been_initialised ) then
       call ProfileInit()
    endif
    print *, "ProfileStart called for module '", module_name,  &
         "' region '", region_name, "'"
    profiler_data%module_name = module_name
    profiler_data%region_name = region_name
  end subroutine ProfileStart

  ! ---------------------------------------------------------------------------
  ! Ends a profiling area. It takes a ProfilerData type that corresponds to
  ! to the ProfileStart call.
  ! profile_data: Persistent data used by the profiling library.
  ! 
  subroutine ProfileEnd(profiler_data)
    implicit none

    type(ProfilerData) :: profiler_data
    
    print *,"ProfileEnd   called for module '", profiler_data%module_name, &
         "' region '", profiler_data%region_name, "'"
  end subroutine ProfileEnd

  ! ---------------------------------------------------------------------------
  subroutine ProfileFinalise()
    implicit none
    print *,"ProfileFinalise called"
    has_been_initialised = .true.
  end subroutine ProfileFinalise

end module profiler_mod
