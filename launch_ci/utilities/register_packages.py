from importlib_metadata import packages_distributions
import launch
if False:
    # imports here would cause loops, but are only used as forward-references for type-checking
    from ..actions import Package


def add_package(context: launch.LaunchContext, name: str, package: 'Package'):
    """Adds a package to the registry.

    :param name: Name of the package
    :param package: Package action associated with name
    """

    context.extend_locals({name: package})
    

def get_package(context: launch.LaunchContext, name: str):
    """Gets package by name

    :param name: Name of the Package
    """
    return context.get_locals_as_dict()[name]