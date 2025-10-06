# TreeScape

TreeScape is a Jupyter-based visualization tool for performance data, enabling
users to programmatically render graphs. With TreeScape, you can load an
ensemble of [Caliper](https://github.com/LLNL/caliper) performance files and
visualize the collective performance of an application across many runs. This
could involve tracking performance changes over time, comparing the performance
achieved by different users, running scaling studies across time, etc.
TreeScape is the replacement for SPOT, which was web-based.

# Documentation

The notebook below provides some examples of how to interact with TreeScape:
`regression_notebooks/NightlyTestDemo_local.ipynb`.

# Getting Involved

TreeScape is an open-source project, and we welcome contributions from the
community.

You can also start an issue for a [bug report or feature] request(https://github.com/LLNL/treescape/issues/new).

# Setup Localhost environment, for development
1) Clone the repository:
```
git clone https://github.com/LLNL/treescape.git
```

2) Create a virtual environment:
```
python3 -m venv venv
```

3) Activate the virtual environment:
```
source venv/bin/activate
```

4) Install the dependencies:
```
pip install -r requirements.txt
```

5) Run the notebook:
To make it easier to reach your notebooks, launch jupyter notebook from the directory where your notebooks are.  
```
jupyter notebook
```
6) Open Notebook
After jupyter notebook is running, open the notebook `regression_notebooks/NightlyTestDemo_local.ipynb`.
You will need to modify the paths to the caliper files to match your local environment.
You will need to modify the following paths too:
sys.path.append("/Users/aschwanden1/min-venv-local/lib/python3.9/site-packages")
sys.path.append("/Users/aschwanden1/github/treescape")

7) Run the cells in the notebook.


# Contributions

We welcome all kinds of contributions: new features, bug fixes, documentation edits; it's all great!

To contribute, make a [pull request](https://github.com/LLNL/treescape/compare),
with `main` as the destination branch.

# Authors

TreeScape was created by Pascal Aschwandan and Matthew LeGendre.

# Release

TreeScape is released under an MIT license. For more details, please see the
[LICENSE](./LICENSE), [COPYRIGHT](./COPYRIGHT) files.

`LLNL-CODE-2010855`
