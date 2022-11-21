import os
from typing import Iterable, List, Optional
import launch
from git import RepositoryDirtyError
from launch import Action, Condition, LaunchContext, SomeActionsType
from launch.utilities import normalize_to_list_of_substitutions
from launch.utilities import perform_substitutions
from launch_ci.utilities import add_system

class System(Action):

    def __init__(
        self,
        *,
        name: str,
        workspace: str,
        packages: Optional[Iterable[SomeActionsType]] = None,
        condition: Optional[Condition] = None
    ) -> None:
        super().__init__(condition=condition)
        self.__workspace = workspace
        self.__name = name
        self.__exp_workspace = None
        self.__system_install_dir = None
        self.__system_build_dir = None
        self.__system_log_dir = None
        self.__system_source_dir = None
        self.__exp_name = None
        self.__repositories = {}
        self.__packages = {}
        self.__logger = launch.logging.get_logger(__name__)
        self.__package_actions = []
        for package in packages:
            self.__package_actions.append(package)

    def _perform_substitutions(self, context: LaunchContext):
        self.__exp_workspace = perform_substitutions(
            context=context,
            subs=normalize_to_list_of_substitutions(self.__workspace)
        )
        self.__exp_name = perform_substitutions(
            context=context,
            subs=normalize_to_list_of_substitutions(self.__name)
        )
        return

    def add_package(self, name: str, package):
        self.__packages[name] = package

    def get_package(self, name: str):
        return self.__packages[name]

    def is_package(self, name: str) -> bool:
        return name in self.__packages.keys()
    
    def get_packages(self):
        return dict(self.__packages)

    def add_repo(self, name: str, path: str, url: str, version: str):
        self.__repositories[name] = {"path": path, "url": url, "version": version}

    def get_repo(self, name: str):
        return self.__repositories[name]

    def is_repo(self, name: str) -> bool:
        return name in self.__repositories.keys()

    def get_repos(self):
        return dict(self.__repositories)

    @property
    def name(self):
        return self.__exp_name

    @property
    def workspace(self):
        return self.__exp_workspace

    @property
    def source_dir(self):
        return self.__system_source_dir

    @property
    def install_dir(self):
        return self.__system_install_dir

    @property
    def build_dir(self):
        return self.__system_build_dir

    @property
    def log_dir(self):
        return self.__system_log_dir

    def execute(self, context: LaunchContext) -> Optional[List[Action]]:
        actions = []
        self._perform_substitutions(context)
        add_system(
            context,
            self.__exp_name,
            self)
        self.__system_source_dir = os.path.join(self.__exp_workspace, "src")
        self.__system_build_dir = os.path.join(self.__exp_workspace, "build")
        self.__system_install_dir = os.path.join(self.__exp_workspace, "install")
        self.__system_log_dir = os.path.join(self.__exp_workspace, "log")
        actions.extend(self.__package_actions)
        return actions
