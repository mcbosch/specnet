# Specnet

`specnet` is a python package focused on Spectral Graph Theory and Network analysis. This package has the same architecture of `networkx` since we want to make an extension of this package that includes:

- **Working with general magnetic graphs and magnetic laplacian**.  Unlike `networkx` we build the laplacian in a more general framework and allowing to define magnetic potentials. 
- **Create Frame Family Graphs**. This graphs allows us to build isospectral example graphs. 

Future work is going to focus on create functions to work with signals on graphs, visualization tools, and spectral methods (further than only computing the spectra).

## Installation
To install the package you can run the following command in the enviorement you want to install the package:

```
pip install specnet
```

If you want to install the last version in github you can run
```
pip install git+https://github.com/mcbosch/specnet.git
```
### Create a Virtual env and Install

If you want to run experiments on your computer and create a virtual enviorment with this package you can create a folder where you want to work, go to that folder and execute the following code on your machine:
#### VSCode Terminal or Windows Powershell
```
> python -m venv env_name
> env_name\Scripts\activate
> pip install specnet
```

#### Linux, MacOS or GitBash
```
$ python -m venv env_name
$ source env_name/Scripts/activate
$ pip install specnet
```

#### Conda
```
> conda create --name env_name python=3.10 
> conda activate env_name
> pip install specnet
```
## References

<a id="1" href="https://doi.org/10.1007/s13324-023-00823-9">[1]</a> Fabila-Carrasco, J.S., Lledó, F. & Post, O. A geometric construction of isospectral magnetic graphs. Anal.Math.Phys. 13, 64 (2023). 


<a id="2" href='https://www.sciencedirect.com/science/article/pii/S0024379518300673'>[2]</a>  Fabila-Carrasco, J.S., Lledó, F., Post, O.: Spectral gaps and discrete magnetic Laplacians. Linear
Algebra Appl. 547, 183–216 (2018). 
