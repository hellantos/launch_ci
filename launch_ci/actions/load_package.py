import os
from pkg_resources import Distribution
import rosdistro
import launch
from launch import Action
from launch import SomeSubstitutionsType
from launch import LaunchContext
from launch import Condition
from launch import EventHandler
from launch.actions import OpaqueFunction
from launch.utilities import normalize_to_list_of_substitutions
from launch.utilities import perform_substitutions

from git import Repo
from typing import Optional, List, cast
from pathlib import Path
from rosdistro import get_index_url, get_index, get_distribution_file

from ..actions import Package
from ..utilities import get_package


class LoadPackage(Action):
    def __init__(
        self, *,
        package_name: SomeSubstitutionsType,
        condition: Optional[Condition] = None
        ) -> None:
        super().__init__(condition=condition)
        self.__package_name = package_name
        self.__exp_package_name = None
        self.__package : Package = None
        self.__repository = None
        self.__logger = launch.logging.get_logger(__name__)

    def _perform_substitutions(self, context):
        self.__exp_package_name = perform_substitutions(
            context=context,
            subs=normalize_to_list_of_substitutions(self.__package_name)
        )

    def _get_index(self) -> rosdistro.Index:
        """Get the rosdistro index.
        """
        distro_url = get_index_url()
        distro_index : rosdistro.Index = get_index(distro_url)
        return distro_index
        

    def _get_distro_env(self) ->  str:
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


    def _fetch_from_distro(self):
        """Load source from a rosdistro package entry.
        """
        distro_index = self._get_index()
        distro_name = self._get_distro_env()
        distro_file = self._get_distro(distro_index, distro_name)
        repository_name: str = None
        if self.__exp_package_name in distro_file.release_packages.keys():
            repository_name = distro_file.release_packages[self.__exp_package_name].repository_name

        
        repository = distro_file.repositories[repository_name]
        if repository.source_repository.type == "git":
            self.__package.url = repository.source_repository.url
            self.__package.version = repository.source_repository.version
            self._fetch_from_git()
        
        return



    def _fetch_from_git(self):
        """Clone package from a git repository.
        """
        if not Path(os.path.join(self.__package.local_path, self.__exp_package_name)).exists():
            self.__repository = Repo.clone_from(self.__package.url, self.__package.local_path)
            self.__repository.remote().fetch()
            for head in self.__repository.heads:
                print(head.name)
            
            # self.__repository.heads[self.__package.version].checkout()

        return

    def _fetch_package(self, context: LaunchContext):

        self.__package = get_package(context, self.__exp_package_name)
        if self.__package.type == "distro":
            self.__logger.info("Fetching {} from distro.".format(self.__package.package_name))
            context.add_completion_future(
                context.asyncio_loop.run_in_executor(
                    None, self._fetch_from_distro
                )
            )
        
        if self.__package.type == "git":
            self.__logger.info("Fetching {} from git.".format(self.__package.package_name))
            context.add_completion_future(
                context.asyncio_loop.run_in_executor(
                    None, self._fetch_from_git
                )
            ) 

    def _on_pkg_created(self, context: LaunchContext):
        typed_event = cast(launch.events.ExecutionComplete, context.locals.event)
        if not hasattr(typed_event.action, "package_name"):
            return
        if typed_event.action.package_name == self.__exp_package_name:
            self._fetch_package(context=context)
 

    def execute(self, context: LaunchContext) -> Optional[List[Action]]:
        self._perform_substitutions(context)
        self.__logger.info("Executing LoadPackage for {}.".format(self.__exp_package_name))

        try:
            get_package(context, self.__exp_package_name)
            self.__logger.info("Direct Fetch.")
            self._fetch_package(context=context)
        except AttributeError:
            event_handler = EventHandler(
                matcher=lambda event: isinstance(event, launch.events.ExecutionComplete),
                entities=[
                    OpaqueFunction(
                        function=self._on_pkg_created
                    )
                ],
                handle_once=True
            )
            context.register_event_handler(event_handler)


        return super().execute(context)