from asyncio.subprocess import PIPE, STDOUT
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
from subprocess import Popen
from ..utilities.register_packages import get_system

class BuildSystem(Action):

    def __init__(
        self, *,
        system_name: SomeSubstitutionsType,
        condition: Optional[Condition] = None
        ) -> None:
        super().__init__(condition=condition)
        self.__system_name = system_name
        self.__exp_system_name = None
        self.__system = None
        self.__logger = launch.logging.get_logger(__name__)
        

    def _perform_substitutions(self, context: LaunchContext):
        self.__exp_system_name = perform_substitutions(
            context=context,
            subs=normalize_to_list_of_substitutions(self.__system_name)
        )


    def execute(self, context: LaunchContext) -> Optional[List[Action]]:
        actions = []
        self._perform_substitutions(context)
        self.__system: System = get_system(context, self.__exp_system_name)
        cmd1 = "source /opt/ros/galactic/setup.bash; colcon build"
        self.__logger.info("Starting to build system {}".format(self.__exp_system_name))
        final = Popen(cmd1, start_new_session=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd=self.__system.workspace, shell=True)
        final.wait()
        self.__logger.info("Finished building system {}".format(self.__exp_system_name))
        return actions