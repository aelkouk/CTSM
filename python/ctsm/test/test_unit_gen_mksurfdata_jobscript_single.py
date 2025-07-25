#!/usr/bin/env python3

"""
Unit tests for gen_mksurfdata_jobscript_single.py subroutines:
"""

import unittest
import os
import shutil

from ctsm import unit_testing
from ctsm.test_gen_mksurfdata_jobscript_single_parent import TestFGenMkSurfJobscriptSingleParent
from ctsm.toolchain.gen_mksurfdata_jobscript_single import get_parser
from ctsm.toolchain.gen_mksurfdata_jobscript_single import check_parser_args
from ctsm.toolchain.gen_mksurfdata_jobscript_single import write_runscript_part1


# Allow test names that pylint doesn't like; otherwise hard to make them
# readable
# pylint: disable=invalid-name


# pylint: disable=protected-access
# pylint: disable=too-many-instance-attributes
class TestFGenMkSurfJobscriptSingle(TestFGenMkSurfJobscriptSingleParent):
    """Tests the gen_mksurfdata_jobscript_single subroutines"""

    def assertFileContentsEqual(self, expected, filepath, msg=None):
        """Asserts that the contents of the file given by 'filepath' are equal to
        the string given by 'expected'. 'msg' gives an optional message to be
        printed if the assertion fails.

        Copied from test_unit_job_launcher_no_batch should go to utils!"""

        with open(filepath, "r") as myfile:
            contents = myfile.read()

        self.assertEqual(expected, contents, msg=msg)

    def test_simple_derecho_args(self):
        """test simple derecho arguments"""
        machine = "derecho"
        nodes = 1
        tasks = 64
        unit_testing.add_machine_node_args(machine, nodes, tasks)
        args = get_parser().parse_args()
        check_parser_args(args)
        with open(self._jobscript_file, "w", encoding="utf-8") as runfile:
            attribs = write_runscript_part1(
                number_of_nodes=nodes,
                tasks_per_node=tasks,
                machine=machine,
                account=self._account,
                walltime=args.walltime,
                runfile=runfile,
            )
            self.assertEqual({"mpilib": "default"}, attribs, msg="attribs not as expected")

        self.assertFileContentsEqual(self._output_compare, self._jobscript_file)

    def test_too_many_tasks(self):
        """test trying to use too many tasks"""
        machine = "derecho"
        nodes = 1
        tasks = 129
        unit_testing.add_machine_node_args(machine, nodes, tasks)
        args = get_parser().parse_args()
        check_parser_args(args)
        with open(self._jobscript_file, "w", encoding="utf-8") as runfile:
            with self.assertRaisesRegex(
                SystemExit,
                "Number of tasks per node exceeds the number of processors per node"
                + " on this machine",
            ):
                write_runscript_part1(
                    number_of_nodes=nodes,
                    tasks_per_node=tasks,
                    machine=machine,
                    account=self._account,
                    walltime=args.walltime,
                    runfile=runfile,
                )

    def test_zero_tasks(self):
        """test for fail on zero tasks"""
        machine = "derecho"
        nodes = 5
        tasks = 0
        unit_testing.add_machine_node_args(machine, nodes, tasks)
        args = get_parser().parse_args()
        with self.assertRaisesRegex(
            SystemExit,
            "Input argument --tasks_per_node is zero or negative and needs to be positive",
        ):
            check_parser_args(args)

    def test_bld_build_path(self):
        """test for bad build path"""
        machine = "derecho"
        nodes = 10
        tasks = 64
        unit_testing.add_machine_node_args(machine, nodes, tasks)
        # Remove the build path directory
        shutil.rmtree(self._bld_path, ignore_errors=True)
        args = get_parser().parse_args()
        with self.assertRaisesRegex(SystemExit, "Input Build path .+ does NOT exist, aborting"):
            check_parser_args(args)

    def test_mksurfdata_exist(self):
        """test fails if mksurfdata does not exist"""
        machine = "derecho"
        nodes = 10
        tasks = 64
        unit_testing.add_machine_node_args(machine, nodes, tasks)
        args = get_parser().parse_args()
        os.remove(self._mksurf_exe)
        with self.assertRaisesRegex(SystemExit, "mksurfdata_esmf executable "):
            check_parser_args(args)

    def test_env_mach_specific_exist(self):
        """test fails if the .env_mach_specific.sh file does not exist"""
        machine = "derecho"
        nodes = 10
        tasks = 64
        unit_testing.add_machine_node_args(machine, nodes, tasks)
        args = get_parser().parse_args()
        os.remove(self._env_mach)
        with self.assertRaisesRegex(SystemExit, "Environment machine specific file"):
            check_parser_args(args)

    def test_bad_machine(self):
        """test bad machine name"""
        machine = "zztop"
        nodes = 1
        tasks = 64
        unit_testing.add_machine_node_args(machine, nodes, tasks)
        with self.assertRaises(SystemExit):
            get_parser().parse_args()


if __name__ == "__main__":
    unit_testing.setup_for_tests()
    unittest.main()
