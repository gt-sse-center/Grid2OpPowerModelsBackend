# Grid2OpPowerModelsBackend

The primary purpose of this project is to build a portable shared library of [PowerModels.jl](https://github.com/lanl-ansi/PowerModels.jl). For our purposes the target consumer is [Grid2Op](https://github.com/Grid2op/grid2op), a Python framework for modeling power grid operations.

CI/CD workflows can be found in the .github/workflows directory. GitHub Actions compile the shared library, then bundle the binaries and update a PyPI package. There is a GitHub Actions secret, `PYPI_API_KEY`, that needs to be set with the PyPI token for this to work.

From the root of this repository, to produce the shared library and build this project:
```shell
cd PowerModelsLibrary
julia --project=. compile_library.jl
cd ..
cp -rf PowerModelsLibrary/libpowermodels src/PowerModelsBackend/shared_objects/
```