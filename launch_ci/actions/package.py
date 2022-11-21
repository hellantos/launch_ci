from typing import Optional
from typing import List

import os
import launch

from launch import Condition
from launch import LaunchContext
from launch import Action
from launch.actions import OpaqueFunction
from launch import SomeSubstitutionsType
from launch.utilities import normalize_to_list_of_substitutions
from launch.utilities import perform_substitutions
from launch_ci.actions.system import System

import rosdistro
from rosdistro import get_index_url, get_index, get_distribution_file

from ..utilities import get_system

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
            system: SomeSubstitutionsType,
            url: Optional[SomeSubstitutionsType] = None,
            condition: Optional[Condition] = None
            ) -> None:
        super().__init__(condition=condition)
        self.__name = name
        self.__type = type
        self.__version = version
        self.__url = url
        self.__system_name = system

        self.__exp_name = None
        self.__exp_type = None
        self.__exp_version = None
        self.__exp_url = None
        self.__exp_system_name = None
        self.__exp_source_path = None
        self.__repository_name = None
        self.__exp_install_path = None
        self.__exp_build_path = None

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
        self.__exp_system_name = perform_substitutions(
            context=context,
            subs=normalize_to_list_of_substitutions(self.__system_name)
        )
        if self.__url is not None:
            self.__url = perform_substitutions(
                context=context,
                subs=normalize_to_list_of_substitutions(self.__url)
            )

    def _get_index(self) -> rosdistro.Index:
        """Get the rosdistro index.
        """
        distro_url = get_index_url()
        distro_index: rosdistro.Index = get_index(distro_url)
        return distro_index

    def _get_distro_env(self) -> str:
        """Get distro from environment
        """
        distro_name = os.environ.get("ROS_DISTRO")
        return distro_name

    def _get_distro(self, index: rosdistro.Index, distro_name: str) -> rosdistro.DistributionFile:
        """Get distribution from index

        :param index: Index
        :param distro_name: Distro name
        :return: Distro object
        """
        if distro_name in index.distributions.keys():
            distro = get_distribution_file(index, distro_name)
        return distro

    def _fetch_from_distro(self, context):
        """Load source from a rosdistro package entry.
        """
        distro_index = self._get_index()
        distro_name = self._get_distro_env()
        distro_file = self._get_distro(distro_index, distro_name)
        repository_name: str = None
        if self.__exp_name in distro_file.release_packages.keys():
            repository_name = distro_file.release_packages[self.__exp_name].repository_name

        repository = distro_file.repositories[repository_name]
        if repository.source_repository.type == "git":
            self.url = repository.source_repository.url
            self.version = repository.source_repository.version
            self.repository_name = repository_name
            repo_path = os.path.join(
                self.__system.source_dir, repository_name)

            if not self.__system.is_repo(repository_name):
                self.__system.add_repo(
                    repository_name, repo_path, self.url, self.version)
            self.__logger.info("Added package {} from repository {}".format(self.__exp_name, repository_name))
        return

    def _fetch_package(self, context: LaunchContext):
        if self.type == "distro":
            return [OpaqueFunction(function=self._fetch_from_distro)]


        if self.type == "git":
            url_parts = self.__exp_url.split("/")
            repo_name = url_parts[len(url_parts)-1].split(".")[0]
            repo_path = os.path.join(self.__system.source_dir, repo_name)
            self.repository_name = repo_name
            self.__logger.info("Added package {} from repository {}".format(self.__exp_name, repo_name))

            if not self.__system.is_repo(repo_name):
                self.__system.add_repo(
                    repo_name, repo_path, self.url, self.version)

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
    def source_path(self) -> str:
        if self.__exp_source_path is None:
            raise AttributeError("local_path is not set.")
        return self.__exp_source_path

    @source_path.setter
    def source_path(self, value: str):
        self.__logger.info("{} is in {}".format(self.name, value))
        self.__exp_source_path = value

    @property
    def repository_name(self):
        if self.__exp_source_path is None:
            raise AttributeError("repository name is not set.")
        return self.__repository_name

    @repository_name.setter
    def repository_name(self, value):
        self.__repository_name = value

    @property
    def install_path(self):
        return self.__install_path

    @property
    def build_path(self):
        return self.__build_path

    def execute(self, context: LaunchContext) -> Optional[List[Action]]:
        self._perfrom_substitutions(context=context)
        self.__system: System = get_system(context, self.__exp_system_name)
        self.__system.add_package(self.__exp_name, self)
        self.__install_path = os.path.join(self.__system.workspace, "install", self.package_name)
        self.__build_path = os.path.join(self.__system.workspace, "build", self.package_name)
        return [OpaqueFunction(function=self._fetch_package)]