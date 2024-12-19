#=
PowerModelsLibrary:
- Julia version: 1.11.1
- Date: 2024-11-21
=#
module PowerModelsLibrary

using PowerModels
using JSON

#=
JuMP models are the fundamental building block that we use to construct optimization problems. They hold things like the variables and constraints, as well as which solver to use and even solution information.
"optimizer" as a synonym for "solver."
supported solvers https://jump.dev/JuMP.jl/stable/installation/#Supported-solvers
=#
# JuMP model reference: https://jump.dev/JuMP.jl/stable/manual/models/

function load_grid(path::String)::Nothing
    # NOTE: in Grid2Op load_grid should be called first, loading the grid representation, and solve_power_flow expects that load_grid has been called and populate Grid2Op's representation (which is housed in the `Backend` property `_grid`).
    # PowerModels.jl actually expects a consolidated call, e.g. solve_opf("matpower/case3.m", Ipopt.Optimizer), which makes load_grid() only useful for populating the Grid2Op representation.
    # PowerModels documentation of this can be found in the quick start: https://lanl-ansi.github.io/PowerModels.jl/stable/quickguide/
    # The PowerModels documentation indicates that only MATPOWER (.m) or PSS/E (.raw) input representations are possible. This is at odds with Grid2Op / RL2Grid NumPy grid representations without conversion (e.g. using PandaPower's Converter.from_mpc() and Converter.to_mpc() for MATPOWER https://pandapower.readthedocs.io/en/latest/converter.html).
    # That said, PowerModels actually represents the grid in JSON format internally (https://lanl-ansi.github.io/PowerModels.jl/stable/network-data/) and "attempts to be similar to matpower case format", which is described here: https://matpower.org/docs/ref/matpower5.0/caseformat.html

    # That is all to say that, while it would be possible to convert the input NumPy to MATPOWER to PowerModels, it would be simpler, and likely therefore faster, to convert directly from Grid2Op's representation to PowerModels representation (see PowerModelsBackend.py grid2op_to_powermodels_json).

    # Useful PowerModels functions follow.
    # In reality all of the following can be replaced with the appropriate one line operation, but solve_ac_opf has been broken down into its comprised operations for debugging purposes:
    # solve_ac_opf("matpower/case3.m", Ipopt.Optimizer)

    # Parse a .raw, .m or .json file - path being the full path to that file
    # in theory if we use load_grid we should store this to an instance property but that does not seem to be necessary since we plan to use solve_power_flow exclusively
    result = PowerModels.parse_file(path)
end

function solve_power_flow(path::String)::String
    #= In reality all of the following can be replaced with the appropriate one line operation, but solve_ac_opf has been broken down into its comprised operations for debugging purposes:
    solve_ac_opf("matpower/case3.m", Ipopt.Optimizer)
    The function solve_ac_opf and solve_dc_opf are shorthands for a more general formulation-independent OPF execution, solve_opf. For example, solve_ac_opf is equivalent to,
    solve_opf("matpower/case3.m", ACPPowerModel, Ipopt.Optimizer)
    https://lanl-ansi.github.io/PowerModels.jl/stable/power-flow/
    The solve_pf solution method is both formulation and solver agnostic and can leverage the wide range of solvers that are available in the JuMP ecosystem. Many of these solvers are commercial-grade, which in turn makes solve_pf the most reliable power flow solution method in PowerModels.
    Use of solve_pf is highly recommended over the other solution methods for increased robustness. Applications that benefit from the Julia native solution methods are an exception to this general rule.
    The advantage of compute_ac_pf over solve_ac_pf is that it does not require building a JuMP model.
    If compute_ac_pf fails to converge try solve_ac_pf instead
    =#

    # Parse a .raw, .m or .json file - path being the full path to that file
    network_data = PowerModels.parse_file(path)

    # Instantiate the model
    pm = instantiate_model(network_data, ACPPowerModel, PowerModels.build_opf)

    # PowerModels facilitates pretty printing in most scenarios, e.g.
    print(pm.model)

    # solver
    result = optimize_model!(pm, optimizer=Ipopt.Optimizer)

    # can also inspect data with raw display
    display(network_data)
    # or, even better, a table-like summary
    PowerModels.print_summary(network_data)

    # or fetch specific component data in matrix form
    # PowerModels.component_table(network_data, "bus", ["vmin", "vmax"])

    # result = PowerModels.run_dc_opf(data, PowerModels.run_dc_opf_default)
    # display detailed output
    print_summary(result["solution"])
    #=
    result format https://lanl-ansi.github.io/PowerModels.jl/stable/network-data/#The-Network-Data-Dictionary
    {
    "optimizer":<string>,    # name of the Julia class used to solve the model
    "termination_status":<TerminationStatusCode enum>, # optimizer status at termination
    "primal_status":<ResultStatusCode enum>, # the primal solution status at termination
    "dual_status":<ResultStatusCode enum>, # the dual solution status at termination
    "solve_time":<float>,    # reported solve time (seconds)
    "objective":<float>,     # the final evaluation of the objective function
    "objective_lb":<float>,  # the final lower bound of the objective function (if available)
    "solution":{...}         # complete solution information (details below)
    }=#
    return JSON.json(result)
end

Base.@ccallable c_load_grid(path::Cstring)::Nothing = load_grid(path)

Base.@ccallable c_solve_power_flow(path::Cstring)::Cstring = solve_power_flow(input_data)

end
