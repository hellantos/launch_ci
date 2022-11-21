    
    
from pathlib import Path
from typing import List, Optional
from rospkg import RosPack
from git import Repo
from launch import Action, Condition, LaunchContext, SomeSubstitutionsType
from launch.actions import OpaqueFunction
import launch
from launch.utilities import normalize_to_list_of_substitutions
from launch.utilities import perform_substitutions
from launch_ci.actions import System
from ..utilities.register_packages import get_system

class CloneSystem(Action):

    def __init__(
        self, *,
        system_name: SomeSubstitutionsType,
        condition: Optional[Condition] = None
        ) -> None:
        super().__init__(condition=condition)
        self.__system_name = system_name
        self.__exp_system_name = None
        self.__system = None
        self.__repos_to_load = {}
        self.__logger = launch.logging.get_logger(__name__)
        

    def _perform_substitutions(self, context: LaunchContext):
        self.__exp_system_name = perform_substitutions(
            context=context,
            subs=normalize_to_list_of_substitutions(self.__system_name)
        )

    def _clone_from_git(self, url, path, version):
        """Clone package from a git repository.
        """

        if not Path(path).exists():
            self.__logger.info("Cloning {}.".format(url))
            self.__repository = Repo.clone_from(url, path)
        else:
            self.__repository = Repo(path)

        self.__logger.info("Checkout repository {} on {}.".format(url, version))
        self.__repository.git.checkout(version)
        self.__repository.git.pull('origin', version)
        return

    def _clone_repositories(self, context):
        if len(self.__repos_to_load) > 0:
            item = self.__repos_to_load.popitem()
            self._clone_from_git(item[1]["url"], item[1]["path"], item[1]["version"])
            return [OpaqueFunction(function=self._clone_repositories)]
        
        self.__logger.info("Searching packages")
        r = RosPack(ros_paths=[self.__system.workspace])
        packages = self.__system.get_packages()
        for key in packages.keys():
            packages[key].source_path = r.get_path(packages[key].package_name)

    def execute(self, context: LaunchContext) -> Optional[List[Action]]:
        actions = []
        self._perform_substitutions(context)
        self.__system: System = get_system(context, self.__exp_system_name)
        self.__repos_to_load = self.__system.get_repos()
        self.__logger.info("Start loading {}".format(self.__system_name))
        actions.append(OpaqueFunction(function=self._clone_repositories))
        return actions