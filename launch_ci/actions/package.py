from typing import Optional
from typing import List

import launch

from launch import Condition
from launch import LaunchContext
from launch import Action
from launch import SomeSubstitutionsType
from launch.utilities import normalize_to_list_of_substitutions
from launch.utilities import perform_substitutions

from ..utilities import add_package

class Package(Action):
    __PACKAGE_TYPE_DISTRO = 1 
    __PACKAGE_TYPE_GIT = 2

    package_types = {
        __PACKAGE_TYPE_DISTRO: "distro",
        __PACKAGE_TYPE_DISTRO: "git"
    }

    @property
    def PACKAGE_TYPE_DISTRO(self):
        return self.package_types[self.__PACKAGE_TYPE_DISTRO]

    @property
    def PACKAGE_TYPE_GIT(self):
        return self.package_types[self.__PACKAGE_TYPE_GIT]

    def __init__(
            self,
            *,
            name: SomeSubstitutionsType,
            type: SomeSubstitutionsType,
            version: SomeSubstitutionsType,
            local_path: SomeSubstitutionsType,
            url: Optional[SomeSubstitutionsType] = None,
            condition: Optional[Condition] = None
            ) -> None:
        super().__init__(condition=condition)
        self.__name = name
        self.__type = type
        self.__version = version
        self.__url = url
        self.__local_path = local_path

        self.__exp_name = None
        self.__exp_type = None
        self.__exp_version = None
        self.__exp_url = None
        self.__exp_local_path = None

        self.__logger = launch.logging.get_logger(__name__)

    def _perfrom_substitutions(self, context: LaunchContext):
        self.__exp_name = perform_substitutions(
            context=context,
            subs=normalize_to_list_of_substitutions(self.__name)
        )
        self.__exp_type = perform_substitutions(
            context=context,
            subs=normalize_to_list_of_substitutions(self.__type)
        )
        self.__exp_version = perform_substitutions(
            context=context,
            subs=normalize_to_list_of_substitutions(self.__version)
        )
        self.__exp_local_path = perform_substitutions(
            context=context,
            subs=normalize_to_list_of_substitutions(self.__local_path)
        )
        if self.__url is not None:
            self.__url = perform_substitutions(
                context=context,
                subs=normalize_to_list_of_substitutions(self.__url)
            )

    @property
    def name(self):
        return self.__exp_name

    @property
    def package_name(self):
        return self.__exp_name

    @property
    def type(self):
        return self.__exp_type

    @type.setter
    def type(self, value: str):
        self.__exp_type = value

    @property
    def version(self):
        return self.__exp_version

    @version.setter
    def version(self, value: str):
        self.__exp_version = value

    @property
    def url(self):
        return self.__exp_url

    @url.setter
    def url(self, value: str):
        self.__exp_url = value

    @property
    def local_path(self):
        return self.__exp_local_path

    def execute(self, context: LaunchContext) -> Optional[List[Action]]:
        self._perfrom_substitutions(context=context)
        self.__logger.info("Adding package {}.".format(self.__exp_name))
        add_package(context, self.__exp_name, self)
        return super().execute(context)