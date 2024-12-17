import os
from typing import Union, Optional, Tuple
import platform
from cffi import FFI
import grid2op


class PowerModelsBackend(grid2op.Backend):
    shunts_data_available = True

    def __init__(self):
        # Initialize the cffi interface for PowerModels shared lib
        ffi = FFI()
        SYSTEM = platform.system().lower()
        SHARED_OBJECTS_DIR = os.path.join(os.path.dirname(__file__), "PowerModelsLibrary", "libpowermodels", "lib",
                                          "julia")
        if SYSTEM == "linux":
            SHARED_OBJECT = os.path.join(SHARED_OBJECTS_DIR, "libpowermodels.so")
        elif SYSTEM == "darwin":
            SHARED_OBJECT = os.path.join(SHARED_OBJECTS_DIR, "libpowermodels.dylib")
        elif SYSTEM == "windows":
            SHARED_OBJECT = os.path.join(SHARED_OBJECTS_DIR, "libpowermodels.dll")
        else:
            raise RuntimeError(f"Unsupported platform: {SYSTEM}")

        # Load the shared library
        self.power_models_lib = ffi.dlopen(SHARED_OBJECT)

        # Declare the function signatures
        ffi.cdef("""
        int c_load_grid(const char* input_data);
        """)
        ffi.cdef("""
        int c_solve_power_flow();
        """)

    def load_grid(self,
                  path: Union[os.PathLike, str],
                  filename: Optional[Union[os.PathLike, str]] = None) -> None:
        # the call to :func:`Backend.load_grid` should guarantee the backend is properly configured
        """
        This is called once at the loading of the powergrid

        It should first define self._grid and then fill all the helpers used by the backend,
        e.g. all the attributes of :class:`Space.GridObjects`

        After the call to :func:`Backend.load_grid` has been performed, the backend should be in such a state where
        the :class:`grid2op.Space.GridObjects` is properly set up

        See the description of :class:`grid2op.Space.GridObjects` to know which attributes should be set here and which should not

        :param path: the path to find the powergrid
        :type path: :class:`string`

        :param filename: the filename of the powergrid
        :type filename: :class:`string`, optional

        :return: ``None``
        """
        full_path = self.make_complete_path(path, filename)
        input_data_c = FFI.new("char[]", full_path.encode("utf-8"))
        status = self.power_models_lib.c_load_grid(input_data_c)

        if status != 0:
            raise RuntimeError(f"PowerModels load_grid failed with status {status}")

        return

    def apply_action(self, backendAction: Union["grid2op.Action._backendAction._BackendAction", None]) -> None:
        # if self.shunts_data_available handle the modification of shunts bus, active value and reactive value
        pass

    def runpf(self) -> Tuple[bool, Union[Exception, None]]:
        status = self.power_models_lib.c_solve_power_flow()

        if status != 0:
            raise RuntimeError(f"PowerModels solve_power_flow failed with status {status}")

        return

    def get_topo_vect(self):
        pass

    def generators_info(self):
        pass

    def loads_info(self):
        pass

    def lines_or_info(self):
        pass

    def lines_ex_info(self):
        pass

    def shunt_info(self):
        pass

    def reset(self):
        """ optional """
        pass

    def close(self):
        """ optional """
        pass

    def copy(self):
        """ optional """
        pass

    def get_line_status(self):
        """ optional """
        pass

    def get_line_flow(self):
        """ optional """
        pass

    def _disconnect_line(self):
        """ optional """
        pass
