# Grid2OpPowerModelsBackend

The primary purpose of this project is to build a portable shared library of [PowerModels.jl](https://github.com/lanl-ansi/PowerModels.jl). For our purposes the target consumer is [Grid2Op](https://github.com/Grid2op/grid2op), a Python framework for modeling power grid operations.

CI/CD workflows can be found in the .github/workflows directory. GitHub Actions compile the shared library, then bundle the binaries for Windows, Linux and MacOS and update a PyPI package. There is a GitHub Actions secret, `PYPI_API_KEY`, that needs to be set with the PyPI token for this to work.

From the root of this repository, to produce the shared library and build this project:
```shell
# enter the Julia source directory
cd PowerModelsLibrary
# create shared libraries from Julia code
julia --project=. compile_library.jl
# copy shared libraries into Python source directory
cd ..
mkdir -p src/PowerModelsBackend/shared_objects/libpowermodels
cp -r PowerModelsLibrary/libpowermodels/lib/julia src/PowerModelsBackend/shared_objects/libpowermodels/
cp PowerModelsLibrary/libpowermodels/lib/libpowermodels.* src/PowerModelsBackend/shared_objects/libpowermodels/
# build Python backend source and deposit into dist directory
python3 -m pip install --upgrade pip build
python3 -m build
# 
```

To use the resulting build locally in another project, check the path of the `.whl` file in the dist directory and install it directly.
```shell
python3 -m pip install Grid2OpPowerModelsBackend-0.1.dev32-py3-none-any.whl
```

Test from Python code:
```python
from PowerModelsBackend import PowerModelsBackend
backend = PowerModelsBackend()
# to test
backend.load_data("path/to/matpower/file.m")
```
