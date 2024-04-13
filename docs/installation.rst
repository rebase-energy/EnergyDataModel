===================
Installation
===================

Requirements
------------

Before installing **EnergyDataModel**, ensure that you have the following:

- Python 3.6 or later
- pip (Python package manager)

Installing with pip
-------------------

To install the latest **stable** release using ``pip``, run the following command in your terminal:

.. code-block:: bash

   pip install energydatamodel


To install the **latest** release from Github: 

.. code-block:: bash

   pip install git+https://github.com/rebase-energy/EnergyDataModel

To install in **editable** mode for development:

.. code-block:: bash

   git clone https://github.com/rebase-energy/EnergyDataModel.git
   cd EnergyDataModel
   pip install -e . 

Verifying Installation
----------------------

To verify that EnergyDataModel has been successfully installed, you can run the following command:

.. code-block:: python

   python -c "import energydatamodel; print(energydatamodel.__version__)"

This should output the installed version of EnergyDataModel.
