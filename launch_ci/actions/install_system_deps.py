    
    
import os
from pathlib import Path
from typing import List, Optional
from rosdep2 import create_default_installer_context
import rosdep2
from rospkg import RosPack
from git import Repo
from launch import Action, Condition, LaunchContext, SomeSubstitutionsType
from launch.actions import OpaqueFunction
import launch
from launch.utilities import normalize_to_list_of_substitutions
from launch.utilities import perform_substitutions
from launch_ci.actions import System
from ..utilities.register_packages import get_system
from rosdep2.main import rosdep_main

class InstallSystemDeps(Action):

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
        rosdep_main(["install", "--ignore-src", "-y", "-r", "-q", "--from-paths", os.path.join(self.__system.workspace, "src")])
        return actions