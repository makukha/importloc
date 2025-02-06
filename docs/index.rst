importloc
=========

.. toctree::
    :maxdepth: 1
    :caption: Details
    :hidden:

    api
    alternatives
    changelog

.. include:: desc.md
    :parser: commonmark

.. include:: badges.md
    :parser: commonmark

.. include:: features.md
    :parser: commonmark


Installation
------------

.. tab-set::

    .. tab-item:: pip

        .. code:: shell

            $ pip install importloc

    .. tab-item:: uv

        .. code:: shell

            $ uv add importloc


Overview
--------

.. currentmodule:: importloc.location

.. autosummary::
    :nosignatures:

    Location
    ModuleLocation
    PathLocation

.. currentmodule:: importloc.util

.. autosummary::
    :nosignatures:

    get_instances
    get_subclasses
    getattr_nested
    random_name


Usage
-----

.. include:: usage.md
    :parser: commonmark

