===============
Getting started
===============

This page should contain a short guide on what the plugin does and
a short example on how to use the plugin.

Installation
++++++++++++

Use the following commands to install the plugin::

    git clone https://github.com/infinitymdm/aiida-spice .
    cd aiida-spice
    pip install -e .  # also installs aiida, if missing (but not postgres)
    # pip install -e .[pre-commit,docs,tests] # install extras for more features
    verdi presto # Set up a new profile
    verdi plugin list aiida.calculations # should now show spice calculations

Then use ``verdi code create`` to set up a spice runner. For example,
to set up ``ngspice`` on the local machine::

    sudo apt install ngspice
    verdi code create core.code.installed --no-wrap-cmdline-params -n \
        -L ngspice \
        -D 45.2 \
        -Y localhost \
        -X $(which ngspice) \
        -P spice.ngspice

Usage
+++++

Here's a quick demo that performs DC operating point analysis on a simple
voltage divider circuit using Xyce::

    verdi daemon start         # make sure the daemon is running
    cd examples
    verdi run voltage_divider.py

You'll need to make sure you have Xyce set up with ``verdi code create``
before running this example. If everything is working correctly, you
should see the DC steady-state voltages for each node displayed as
output.

Take a look at voltage_diveder.py to see how the job is set up.

Available calculations
++++++++++++++++++++++

.. aiida-calcjob:: NgspiceCalculation
    :module: aiida_spice.calculations.ngspice

.. aiida-calcjob:: XyceCalculation
    :module: aiida_spice.calculations.xyce
