Quick start tutorial
--------------------

The main functionality of the **xrdtools** package is to read `*.xrdml` files. This can be
easily achieved by running the following code, e.g. in a ipython prompt:

.. code-block:: python

    import xrdtools

    data = xrdtools.read_xrdml('foo.xrdml')

The data returned from :func:`xrdtools.read_xrdml` is stored in a :obj:`dict`. In case of a simple line scan
(e.g. *2theta-omega* scan) we can get the *xy* data as simple as:

.. code-block:: python

    x = data['x']
    y = data['data']

And plot it for example with :py:mod:`matplotlib.pyplot`:

.. code-block:: python

    from matplotlib import pyplot as plt

    plt.plot(x, y)
    plt.show()


Command line tool
-----------------

Together with the xrdtools package a command line tool ``xrdml`` is installed. It allows to extract
the recorded data from `*.xrdml` files into text files or the command prompt.

Export data into a text file:

.. code-block:: bash

    $ xrdml my_xrdml_file.xrdml #another_file.xrdml ...

In case `my_xrdml_file.xrdml` is a simpe `2Theta-Omega` scan, this will create a text file with two
columns, one for the `2Theta` angles and one for the `Intensity`.

Export data to the prompt:

.. code-block:: bash

    $ xrdml my_xrdml_file.xrdml -o stdout

    # 2Theta-Omega  Intensity
    1.500000000000000000e+01        9.000000000000000222e-01
    1.501869158878504606e+01        5.999999999999999778e-01
    ...

The type of delimiter can be changed with the ``--delimiter`` keyword argument:

.. code-block:: bash

    $ xrdml my_xrdml_file.xrdml -o stdout --delimiter=','

    # 2Theta-Omega,Intensity
    1.500000000000000000e+01,9.000000000000000222e-01
    1.501869158878504606e+01,5.999999999999999778e-01
    ...


