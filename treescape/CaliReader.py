# Copyright 2025 Lawrence Livermore National Security, LLC and other
# Thicket Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: MIT

import json
from glob import glob
import os
from collections import defaultdict
import statistics
import multiprocessing
import sys

import caliperreader as cr
from .Reader import Reader
from .CaliMapMaker import CaliMapMaker

import copy


def pretty_print(str):
    pretty_json = json.dumps(str, indent=4)
    print(pretty_json)


class Node:
    def __init__(self, value):
        self.value = value
        self.children = {}
        self.duration = 0

    def add_child(self, value):
        if value not in self.children:
            self.children[value] = Node(value)
        return self.children[value]

    def __repr__(self):
        return f"Node({self.value}, children={list(self.children.keys())}, duration={self.duration})"


class CaliReader(Reader):

    def __init__(self, path="", pool_size=10, inclusive_strings=None):

        self.pool_size = pool_size
        self.path = path
        self.mapMaker = CaliMapMaker()

        self.entireForest = {"nodes": {}}

        self.inclusive_strings = [
            "min#inclusive#sum#time.duration",
            "max#inclusive#sum#time.duration",
            "avg#inclusive#sum#time.duration",
            "sum#inclusive#sum#time.duration",
        ]

        if inclusive_strings is not None:
            self.inclusive_strings = inclusive_strings

        self.xy_idx_by_drill_level = {}
        self.init()

    def __iter__(self):
        self.keys = list(
            self.xy_idx_by_drill_level.keys()
        )  # Convert keys to a list for indexing
        self.index = 0
        return self

    def __next__(self):
        if self.index < len(self.keys):
            key = self.keys[self.index]
            self.index += 1
            return key, self.xy_idx_by_drill_level[key]  # Return key-value pair
        else:
            raise StopIteration

    def process_profile(profile, var1, var2):
        # Dummy function to process a profile with additional variables
        # Replace with actual processing logic
        return f"Processed {profile} with var1={var1} and var2={var2}"

    def group_profiles(self, profiles, pool_size):
        # Function to evenly distribute profiles among the processes
        grouped_profiles = [[] for _ in range(pool_size)]
        for i, profile in enumerate(profiles):
            grouped_profiles[i % pool_size].append(profile)
        return grouped_profiles

    def combine_objects(self, sobjects):
        combined = {}

        for obj in sobjects:
            for key, value in obj.items():
                if key not in combined:
                    combined[key] = {"xaxis": [], "ydata": []}

                combined[key]["xaxis"].extend(value["xaxis"])
                combined[key]["ydata"].extend(value["ydata"])

        return combined

    def combine_and_setup(self, xaxis):
        nibp3 = self.combine_and_sort_x_and_y(xaxis, self.xy_idx_by_drill_level)

        self.entireForest["nodes"][xaxis] = self.convert_dict_to_array(nibp3)
        # pp = json.dumps( self.entireForest, indent=4 )
        # print(pp)

    def init(self):
        #  0.263s to load 100
        #  2.8s to load 1K          New version 1.067
        #  28 seconds to load 10,000.       60 seconds (i thin most of it was after combining)

        if self.path != "":
            PATH = self.path
        else:
            print("Path must be defined.")

        # PATH = '/Users/aschwanden1/lulesh_gen/1000b/'
        profiles = None
        msg = "For path: " + PATH + ".  "

        try:
            if os.path.exists(PATH) and os.path.isdir(PATH):
                profiles = [
                    y for x in os.walk(PATH) for y in glob(os.path.join(x[0], "*.cali"))
                ]
            else:
                print(msg + "Invalid or non-existent directory.")
                sys.exit()
        except PermissionError:
            print(msg + "Permission denied to access some directories.")
            sys.exit()
        except Exception as e:
            print(msg + f"An error occurred: {e}")
            sys.exit()

        self.first_profile = profiles[0]

        self.r = cr.CaliperReader()
        self.r.read(self.first_profile)

        # new multi processing implementation.
        pool_size = self.pool_size  # Number of processes to use in the pool
        grouped_profiles = self.group_profiles(profiles, pool_size)

        # Create a list of arguments to pass to starmap
        # Initialize an empty list to store the arguments
        args = []

        # Iterate over each group in grouped_profiles
        for group in grouped_profiles:
            # For each group, iterate over each profile
            for profile in group:
                # Create a tuple with profile, self.xaxis,
                # before we used self.xaxis, now that's no longer necessary
                arg = (profile, "")

                # Append the tuple to the args list
                args.append(arg)

        # Now, split args into sublists of size pool_size
        args = [args[i : i + pool_size] for i in range(0, len(args), pool_size)]

        # Flatten the 2D args list back into a 1D list of tuples
        # flattened_args = [item for sublist in args for item in sublist]

        #  The starmap() function takes the name of a function to apply and an iterable.
        #  It will then convert the provided iterable into a list and issue one task for each item in the iterable.
        with multiprocessing.Pool(pool_size) as pool:
            results = pool.starmap(self.read_many_files_wrapper, args)

        results = self.combine_objects(results)

        self.meta_globals = self.get_meta_globals()
        self.xy_idx_by_drill_level = results

        #pretty_json = json.dumps(self.xy_idx_by_drill_level, indent=4)
        #print(pretty_json)
        #exit()

    def read_many_files_wrapper(self, *args):
        return self.read_many_files(*args, inclusive_strings=self.inclusive_strings)

    def read_many_files(self, *several_tuples, inclusive_strings):

        each_res = []

        for tuple in several_tuples:
            one_file = self.read_one_file(tuple[0], inclusive_strings)
            # print('----------------------------------')
            # print(one_file)
            each_res.append(one_file)

        # still need to combine and return it.
        total_dict = self.combine_my_objects(each_res)
        return total_dict

    def combine_my_objects(self, array0):
        combined_data = {}

        for obj in array0:
            for key, data in obj.items():
                xaxis = data["xaxis"][0]
                ydata = data["ydata"][0]

                if key not in combined_data:
                    combined_data[key] = {
                        "name": data["name"],
                        "xaxis": [],
                        "ydata": [],
                    }

                # Check if this xaxis already exists for this key
                if xaxis in combined_data[key]["xaxis"]:
                    index = combined_data[key]["xaxis"].index(xaxis)
                    # combined_data[key]['ydata'][index] += ydata
                    for subkey, value in ydata.items():
                        if subkey in combined_data[key]["ydata"][index]:
                            combined_data[key]["ydata"][index][subkey] += value
                        else:
                            combined_data[key]["ydata"][index][subkey] = value

                else:
                    combined_data[key]["xaxis"].append(xaxis)
                    combined_data[key]["ydata"].append(ydata)

        return combined_data

    def read_one_file(self, cali_file, inclusive_strings):

        r = cr.CaliperReader()
        r.read(cali_file)
        nodes_idx_by_path = {}

        glob0 = cr.read_caliper_globals(cali_file)

        for rec in r.records:
            if "path" in rec:
                path = rec["path"][-1]

                if path not in nodes_idx_by_path:
                    nodes_idx_by_path[path] = {"name": path, "xaxis": [], "ydata": []}

                nodes_idx_by_path[path]["xaxis"].append(glob0)

                for i in range(4):  # 0 to 3
                    if i >= len(rec):  # Avoid index out of range error
                        print(
                            f"rec doesn't have string at index {inclusive_strings[i]}"
                        )
                        sys.exit()
                    if (
                        inclusive_strings[i] not in rec
                    ):  # Check if the string exists and is not empty
                        print(
                            f"rec doesn't have string at index {inclusive_strings[i]}"
                        )
                        sys.exit()

                nodes_idx_by_path[path]["ydata"].append(
                    {
                        "min": rec[inclusive_strings[0]],
                        "max": rec[inclusive_strings[1]],
                        "avg": rec[inclusive_strings[2]],
                        "sum": rec[inclusive_strings[3]],
                    }
                )

                # nodes_idx_by_path[path]["ydata"].append( float(rec["avg#inclusive#sum#time.duration"]) )

        return nodes_idx_by_path

    def custom_sort_key(self, value):
        try:
            # Try to convert the value to a float (works for both ints and numeric strings)
            return (0, float(value))
        except ValueError:
            # If conversion fails, treat it as a string
            return (1, value)

    def combine_and_sort_x_and_y(self, xaxis, nibp):

        nibp2 = copy.deepcopy(nibp)

        for path in nibp2:

            nxy = nibp2[path]

            # Combine xaxis and ydata into a list of tuples
            combined = list(zip(nxy["xaxis"], nxy["ydata"]))

            # Sort the combined list based on xaxis values
            # xaxis is something like 'launchdate' or 'problem_size' etc.

            #  We used to do sorting here but now:
            #  Let the user sort it themselves.
            # combined.sort(key=lambda pair: self.custom_sort_key(pair[0][xaxis]))

            # Initialize a dictionary to hold the ydata statistics for each unique xaxis value
            grouped_data = defaultdict(list)

            # pretty_json = json.dumps(self.xy_idx_by_drill_level, indent=4)
            # print(pretty_json)
            # exit()

            # Group the ydata by their corresponding xaxis value and calculate statistics
            for x, y in combined:
                # print('results -->')
                # print(xaxis)
                # print('x=')
                # print(x)
                sval = x[xaxis]
                grouped_data[sval].append(y)

            # Create the new xaxis and ydata lists
            new_xaxis = []
            new_ydata = []

            for x, ylist in grouped_data.items():
                new_xaxis.append(int(x))
                y_sum = sum(ylist)
                y_avg = statistics.mean(ylist)
                y_min = min(ylist)
                y_max = max(ylist)
                new_ydata.append(
                    {"sum": y_sum, "avg": y_avg, "min": y_min, "max": y_max}
                )

            # Update the original data dictionary
            nxy["xaxis"] = new_xaxis
            nxy["ydata"] = new_ydata
            nxy["name"] = path

        return nibp2

    def convert_dict_to_array(self, obj):
        if not isinstance(obj, dict):
            raise ValueError("Input should be a dictionary.")

        return list(obj.values())

    def build_tree(self, json_data):
        root = Node("root")
        for item in json_data:
            if "function" in item:
                function_path = item["function"]
                duration = item["avg#inclusive#sum#time.duration"]
                current_node = root

                for part in function_path.split("/"):
                    current_node = current_node.add_child(part)
                current_node.duration = duration

        return root

    def print_tree(self, node, level=0):
        print("  " * level + f"{node.value}: {node.duration}")
        for child in node.children.values():
            self.print_tree(child, level + 1)

    def get_meta_globals(self):

        glob0 = cr.read_caliper_globals(self.first_profile)
        meta_globals = {}

        for key in glob0:
            type = self.r.attribute(key).get("adiak.type")
            meta_globals[key] = type

        return meta_globals

    def get_entire(self):

        # self.combine_and_setup( xaxis )

        self.make_child_map()
        cm = self.mapMaker.getChildrenMap()

        return {
            "meta_globals": self.meta_globals,
            "nodes": self.xy_idx_by_drill_level,
            "childrenMap": cm,
        }

    def make_child_map(self):

        for rec in self.r.records:
            if "path" in rec:
                if not isinstance(rec["path"], str):
                    self.mapMaker.make(rec["path"])
