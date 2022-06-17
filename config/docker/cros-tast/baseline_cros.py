#!/usr/bin/env python3
#
# Copyright (C) 2022 Collabora Limited
# Author: Denys Fedoryshchenko <denys.f@collabora.com>
#
# This script is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
import paramiko
import subprocess
import sys

loglevels = ["crit", "alert", "emerg", "err", "warn"]
keyfile = '/home/cros-tast/.ssh/id_rsa'


def report_lava(testname, result, count):
    """
    Report test state/result to LAVA,
    Arguments:
    result: string, should contain fail or pass
    count: integer, number of error lines
    """
    opts = ['lava-test-case', testname, '--result', result, '--units',
            'lines', '--measurement', str(count)]
    subprocess.run(opts)


def fetch_dut():
    output = subprocess.check_output("lava-target-ip", shell=True).strip()
    return output


def run_tests():
    host = fetch_dut()
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_system_host_keys()
    client.connect(host, username="root", key_filename=keyfile)
    for lvl in loglevels:
        _stdin, _stdout, _stderr = client.exec_command(" dmesg --level="
                                                       +lvl+" --notime -x -k")
        buffer = _stdout.read().decode()
        count = len(buffer)
        if not count:
            report_lava("dmesg."+lvl, "pass", count)
        else:
            print(buffer)
            report_lava("dmesg."+lvl, "fail", count)
    client.close()


if __name__ == '__main__':
    run_tests()
