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

    def grid2op_to_powermodels_json(self):
        """
        Convert a Grid2Op backend _grid object to PowerModels JSON
        """

        power_models_json = {
            "version": "2.0",  # PowerModels version
            "buses": [],
            "generators": [],
            "branches": [],
            "loads": [],
            "transformers": [],
        }

        # Extract buses (nodes) from Grid2Op _grid
        for bus in self._grid.get_buses():
            bus_data = {
                "bus_id": bus.id,  # Unique ID for each bus
                "bus_type": 1 if bus.is_slack else 3,  # Slack bus type = 1, Load bus type = 3
                "pd": bus.load.p,  # Active power demand (load) in MW
                "qd": bus.load.q,  # Reactive power demand (load) in MVAR
                "gs": 0.0,  # Shunt conductance (if available)
                "bs": 0.0,  # Shunt susceptance (if available)
                "voltage_magnitude": 1.0,  # Default voltage magnitude (1.0 per unit)
                "voltage_angle": 0.0,  # Voltage angle (0 per unit)
            }
            power_models_json["buses"].append(bus_data)

        # Extract generators (plants) from Grid2Op _grid
        for gen in self._grid.get_generators():
            gen_data = {
                "gen_id": gen.id,
                "bus_id": gen.bus.id,  # The bus to which this generator is connected
                "pg": gen.p,  # Active power generation in MW
                "qg": gen.q,  # Reactive power generation in MVAR
                "pg_max": gen.max_p,  # Maximum active power generation in MW
                "pg_min": gen.min_p,  # Minimum active power generation in MW
                "qg_max": gen.max_q,  # Maximum reactive power generation in MVAR
                "qg_min": gen.min_q,  # Minimum reactive power generation in MVAR
                "cost": 0.0,  # Generator cost (could be added if available)
            }
            power_models_json["generators"].append(gen_data)

        # Extract branches (lines) from Grid2Op _grid
        for branch in self._grid.get_branches():
            branch_data = {
                "branch_id": branch.id,
                "from_bus": branch.from_bus.id,  # From bus ID
                "to_bus": branch.to_bus.id,  # To bus ID
                "r": branch.resistance,  # Resistance in ohms
                "x": branch.reactance,  # Reactance in ohms
                "b": branch.susceptance,  # Susceptance in siemens
                "rateA": branch.rate,  # Thermal rating (MW)
            }
            power_models_json["branches"].append(branch_data)

        # Extract loads (if applicable) from Grid2Op _grid
        for bus in self._grid.get_buses():
            if bus.load is not None:  # Only include buses with loads
                load_data = {
                    "bus_id": bus.id,
                    "pd": bus.load.p,  # Active power load (MW)
                    "qd": bus.load.q,  # Reactive power load (MVAR)
                }
                power_models_json["loads"].append(load_data)

        # Extract transformers (if applicable) from Grid2Op _grid
        for transformer in self._grid.get_transformers():
            transformer_data = {
                "transformer_id": transformer.id,
                "from_bus": transformer.from_bus.id,
                "to_bus": transformer.to_bus.id,
                "tap_ratio": transformer.tap_ratio,  # Tap ratio for voltage transformation
            }
            power_models_json["transformers"].append(transformer_data)

        return power_models_json

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
