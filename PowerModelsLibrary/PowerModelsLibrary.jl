#=
PowerModelsLibrary:
- Julia version: 1.11.1
- Date: 2024-11-21
=#
module PowerModelsLibrary

using PowerModels
using JSON

#  JuMP model https://jump.dev/JuMP.jl/stable/manual/models/
#=
JuMP models are the fundamental building block that we use to construct optimization problems. They hold things like the variables and constraints, as well as which solver to use and even solution information.
"optimizer" as a synonym for "solver."
supported solvers https://jump.dev/JuMP.jl/stable/installation/#Supported-solvers
=#

function load_grid(path::String)::Nothing
    # https://lanl-ansi.github.io/PowerModels.jl/stable/quickguide/
    # path e.g. "matpower/case3.m" or "pti/case3.raw"
    network_data = PowerModels.parse_file(path)

    # network format dictionary to facilitate json serialization https://lanl-ansi.github.io/PowerModels.jl/stable/network-data/
    # attempts to be similar to matpower case format https://matpower.org/docs/ref/matpower5.0/caseformat.html
    # for .raw refer to PSS(R)E v33 specification

    # or separate model building and solving
    #pm = instantiate_model(path, ACPPowerModel, PowerModels.build_opf)
    #print(pm.model)
    #result = optimize_model!(pm, optimizer=Ipopt.Optimizer)

    # or can further break it up by parsing a file into a network data dictionary
    network_data = PowerModels.parse_file(path)
    pm = instantiate_model(network_data, ACPPowerModel, PowerModels.build_opf)
    print(pm.model)
    result = optimize_model!(pm, optimizer=Ipopt.Optimizer)

    # can also inspect data with...
    # display(network_data) # raw dictionary
    PowerModels.print_summary(network_data) # quick table-like summary
    # PowerModels.component_table(network_data, "bus", ["vmin", "vmax"]) # component data in matrix form
end

function solve_power_flow()::String

    # solve_ac_opf("matpower/case3.m", Ipopt.Optimizer)
    # solve_ac_opf("case3.raw", Ipopt.Optimizer)
    #=
    The function solve_ac_opf and solve_dc_opf are shorthands for a more general formulation-independent OPF execution, solve_opf. For example, solve_ac_opf is equivalent to,
    solve_opf("matpower/case3.m", ACPPowerModel, Ipopt.Optimizer)

    https://lanl-ansi.github.io/PowerModels.jl/stable/power-flow/
    The solve_pf solution method is both formulation and solver agnostic and can leverage the wide range of solvers that are available in the JuMP ecosystem. Many of these solvers are commercial-grade, which in turn makes solve_pf the most reliable power flow solution method in PowerModels.
    Use of solve_pf is highly recommended over the other solution methods for increased robustness. Applications that benefit from the Julia native solution methods are an exception to this general rule.
    =#

    # advantage of compute_ac_pf over solve_ac_pf is that it does not require building a JuMP model
    # If compute_ac_pf fails to converge try solve_ac_pf instead.

    # result = PowerModels.run_dc_opf(data, PowerModels.run_dc_opf_default)
    result = solve_power_flow()
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

Base.@ccallable function c_load_grid(path::Cstring)::Cint
    load_grid(path)
end

export load_grid

Base.@ccallable function c_solve_power_flow()::Cstring
    solve_power_flow(input_data)
end

export solve_power_flow

end
