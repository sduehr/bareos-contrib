#!/usr/bin/env python
# -*- coding: utf-8 -*-
# BAREOS - Backup Archiving REcovery Open Sourced
#
# Copyright (C) 2014-2021 Bareos GmbH & Co. KG
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of version three of the GNU Affero General Public
# License as published by the Free Software Foundation, which is
# listed in the file LICENSE.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#
# Author: Stephan Duehr
#
# Bareos python plugins class that adds files from a local list to
# the backup fileset

import bareosfd

# from bareos_fd_consts import bJobMessageType, bFileType, bRCs, bIOPS
import os
from stat import S_IFREG, S_IFDIR, S_IRWXU
import string
import random
import collections
from sys import version_info
import BareosFdPluginBaseclass


class BareosFdPluginGenRandomFiles(BareosFdPluginBaseclass.BareosFdPluginBaseclass):
    """
    Simple Bareos-FD-Plugin-Class that generates random file names
    for testing purposes
    """

    def __init__(self, plugindef):
        bareosfd.DebugMessage(
            100,
            "Constructor called in module %s with plugindef=%s\n"
            % (__name__, plugindef),
        )
        # Last argument of super constructor is a list of mandatory arguments
        super(BareosFdPluginGenRandomFiles, self).__init__(
            plugindef, mandatory_options=["levels", "topdir"]
        )
        self.files_to_backup = []
        self.rndfg = None

    def start_backup_job(self):
        """
        At this point, plugin options were passed and checked already.
        We try to read from filename and setup the list of file to backup
        in self.files_to_backup
        """

        bareosfd.DebugMessage(
            100,
            "Generating filenames at topdir %s with levels %s\n"
            % (self.options["topdir"], self.options["levels"]),
        )
        self.rndfg = GenRandomFiles(self.options["levels"], self.options["topdir"])
        (l1, l2, l3, l4) = self.rndfg.levels
        bareosfd.JobMessage(
            bareosfd.M_INFO,
            "Generating %d * %d * %d * %d = %d Testfiles ...\n"
            % (
                l1,
                l2,
                l3,
                l4,
                l1 * l2 * l3 * l4,
            ),
        )

        self.files_to_backup = self.rndfg.gen_testfiles()

        if not self.files_to_backup:
            bareosfd.JobMessage(
                bareosfdM_ERROR,
                "No (allowed) files to backup found\n",
            )
            return bareosfd.bRC_Error

        return bareosfd.bRC_OK

    def start_backup_file(self, savepkt):
        """
        Defines the file to backup and creates the savepkt. In this example
        only files (no directories) are allowed
        """
        bareosfd.DebugMessage(100, "start_backup_file() called\n")
        if not self.files_to_backup:
            bareosfd.DebugMessage(100, "No files to backup\n")
            return bareosfd.bRC_Skip

        file_to_backup = self.files_to_backup.pop()
        bareosfd.DebugMessage(100, "file: " + file_to_backup + "\n")

        statp = bareosfd.StatPacket()

        if file_to_backup.endswith("/"):
            statp.st_mode = S_IRWXU | S_IFDIR
            savepkt.statp = statp
            savepkt.fname = file_to_backup.rstrip("/")
            savepkt.type = bareosfd.FT_DIREND
            # set link field of savepkt with a trailing '/'
            savepkt.link = file_to_backup
            savepkt.no_read = True

        else:
            statp.st_mode = S_IRWXU | S_IFREG
            statp.st_size = 0
            savepkt.statp = statp
            savepkt.fname = file_to_backup
            savepkt.type = bareosfd.FT_REG

        # bareosfd.JobMessage(
        #     bJobMessageType["M_INFO"],
        #     "Starting backup of %s\n" % (file_to_backup),
        # )
        return bareosfd.bRC_OK

    def end_backup_file(self):
        """
        Here we return 'bRC_More' as long as our list files_to_backup is not
        empty and bRC_OK when we are done
        """
        bareosfd.DebugMessage(100, "end_backup_file() entry point in Python called\n")
        if self.files_to_backup:
            return bareosfd.bRC_More
        else:
            return bareosfd.bRC_OK

    def end_backup_job(self):
        """
        Called if backup job ends, before ClientAfterJob
        Overload this to arrange whatever you have to do at this time.
        """
        self.files_to_backup = []
        self.rndfg = None
        return bareosfd.bRC_OK

    def plugin_io(self, IOP):
        bareosfd.DebugMessage(100, "plugin_io called with function %s\n" % (IOP.func))
        bareosfd.DebugMessage(100, "FNAME is set to %s\n" % (self.FNAME))

        if IOP.func == bareosfd.IO_OPEN:
            self.FNAME = IOP.fname
            try:
                if IOP.flags & (os.O_CREAT | os.O_WRONLY):
                    bareosfd.DebugMessage(
                        100,
                        "Simulating open file %s for writing with %s\n"
                        % (self.FNAME, IOP),
                    )

                #                    dirname = os.path.dirname(self.FNAME)
                #                    if not os.path.exists(dirname):
                #                        bareosfd.DebugMessage(
                #                            100,
                #                            "Directory %s does not exist, creating it now\n"
                #                            % (dirname),
                #                        )
                #                        os.makedirs(dirname)
                #                    self.file = open(self.FNAME, "wb")
                else:
                    bareosfd.DebugMessage(
                        100,
                        "Simulating open file %s for reading with %s\n"
                        % (self.FNAME, IOP),
                    )
                    # self.file = open(self.FNAME, "rb")
            except:
                IOP.status = -1
                return bareosfd.bRC_Error

            return bareosfd.bRC_OK

        elif IOP.func == bareosfd.IO_CLOSE:
            bareosfd.DebugMessage(100, "Simulating Closing file " + "\n")
            # self.file.close()
            return bareosfd.bRC_OK

        elif IOP.func == bareosfd.IO_SEEK:
            return bareosfd.bRC_OK

        elif IOP.func == bareosfd.IO_READ:
            bareosfd.DebugMessage(
                200,
                "Simulating reading %d from file %s\n" % (IOP.count, self.FNAME),
            )
            # IOP.buf = bytearray(IOP.count)
            IOP.buf = bytearray(0)
            # IOP.status = self.file.readinto(IOP.buf)
            IOP.status = 0
            IOP.io_errno = 0
            return bareosfd.bRC_OK

        elif IOP.func == bareosfd.IO_WRITE:
            bareosfd.DebugMessage(
                200, "Simulating writing buffer to file %s\n" % (self.FNAME)
            )
            # self.file.write(IOP.buf)
            IOP.status = IOP.count
            IOP.io_errno = 0
            return bareosfd.bRC_OK


class GenRandomFiles(object):
    def __init__(self, levels, topdir, with_filecontent=False, filesize=0):
        self.levels = [int(s) for s in levels.split(",")]
        self.topdir = topdir
        if version_info.major < 3:
            self.alphabet = string.letters + string.digits
        else:
            self.alphabet = string.ascii_letters + string.digits
        self.alphabet_length = len(self.alphabet)

    def randstring(self, length):
        return "".join(
            [self.alphabet[int(random.random() * 62)] for _ in range(length)]
        )

    def randstrings(self, n, length):
        return [self.randstring(length) for _ in range(n)]

    def randstrings_randlengths(self, n, lmin, lmax):
        rand_strings = []
        length_counts = collections.defaultdict(int)
        lengths = [random.randint(lmin, lmax) for _ in range(n)]
        for length in lengths:
            length_counts[length] += 1
        for length in length_counts:
            rand_strings.extend(self.randstrings(length_counts[length], length))

        return rand_strings

    def gen_testfiles(self):
        (l1, l2, l3, l4) = self.levels
        file_count = 0
        files = []

        # this seeds the random number generator
        # otherwise each subprocess generates the same random numbers. See
        # http://stackoverflow.com/questions/12915177/same-output-in-different-workers-in-multiprocessing
        random.seed()

        files.append(self.topdir + "/")
        for i in range(1, l1 + 1):
            di = "%d-%s" % (i, self.randstring(15))
            files.append(os.path.join(self.topdir, di) + "/")
            for j in range(1, l2 + 1):
                dj = "%d-%s" % (j, self.randstring(random.randint(20, 30)))
                files.append(os.path.join(self.topdir, di, dj) + "/")
                for k in range(1, l3 + 1):
                    # print "i=%d j=%d, k=%d" % (i, j, k)
                    dk = "%d-%s" % (k, self.randstring(random.randint(30, 40)))
                    subdir_name = "%s/%s/%s" % (di, dj, dk)
                    dir_name = os.path.join(self.topdir, subdir_name)
                    files.append(dir_name + "/")
                    file_names = self.randstrings_randlengths(l4, 10, 70)
                    for file_name in file_names:
                        file_count += 1
                        files.append(dir_name + "/" + file_name)

        return files


# vim: ts=4 tabstop=4 expandtab shiftwidth=4 softtabstop=4
