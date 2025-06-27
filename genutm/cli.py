import argparse
import logging

from .cloudinit import CloudInit
from .config import ConfigYAML
from .log import set_root_logger
from .mkuser import MkUser
from .utm import UTM

from . import __version__ as pkg_version


class CLI:
    def __init__(self):
        self.logger = None

        self.args = None
        self.subparsers = None

    # - - parsing - - #
    def _mkuser_args(self):
        mkuser_subparser_desc = "create a UserSpec yaml to be consumed by --userspec"

        self.subparsers.add_parser(
            "mkuser", help=mkuser_subparser_desc, description=mkuser_subparser_desc
        )

    def _create_args(self):
        create_subparser_desc = "create a cloud-init iso"
        create_subparser_vmspec_help = "yaml file holding the vm config"
        create_subparser_userspec_help = "yaml file holding the user config"
        create_subparser_userdata_help = "cloud-init user-data file"

        create_subparser = self.subparsers.add_parser(
            "create", help=create_subparser_desc, description=create_subparser_desc
        )

        create_subparser.add_argument(
            "vmspec_file",
            help=create_subparser_vmspec_help,
        )

        create_subparser.add_argument(
            "--userdata",
            dest="userdata_file",
            required=False,
            help=create_subparser_userdata_help,
        )

        create_subparser.add_argument(
            "--users",
            dest="userspec_file",
            required=False,
            help=create_subparser_userspec_help,
        )

    def _gen_args(self):
        parser_desc = (
            f"genutm UTM bundle and cloud-init ISO generator ver. {pkg_version}"
        )
        parser_d_help = "enable debugging"

        parser = argparse.ArgumentParser(description=parser_desc)
        parser.add_argument("-d", dest="debug", action="store_true", help=parser_d_help)

        self.subparsers = parser.add_subparsers(dest="command", required=True)

        self._create_args()
        self._mkuser_args()
        self.args = parser.parse_args()

    def _create(self):
        config = ConfigYAML(
            self.args.vmspec_file,
            self.args.userspec_file,
            self.args.userdata_file,
        )
        config.run()

        if not self.args.userspec_file and not self.args.userdata_file:
            err_msg = "no users or user-data file was provided, bailing out as "
            err_msg += "you may be unable to log in to an VMs created"
            self.logger.error(err_msg)

        utm = UTM(config.vmspec)
        utm.mkvm()

        clinit = CloudInit(config.vmspec)
        clinit.iso_path = f"{utm.data_dir}/cidata.iso"
        clinit.mkiso()

    # - - main - - #
    def run(self):
        self._gen_args()

        set_root_logger(self.args.debug)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.logger.info("started genutm ver. %s", pkg_version)

        # - - mkuser - - #
        if self.args.command == "mkuser":
            mku = MkUser()
            return mku.run()

        if self.args.command == "create":
            self._create()


def run():
    c = CLI()
    c.run()
