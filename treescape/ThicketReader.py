# Copyright 2025 Lawrence Livermore National Security, LLC and other
# Thicket Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: MIT

# ThicketReader.py
import platform
from glob import glob
import os

from .MyTimer import MyTimer


input_deploy_dir_str = "/usr/gapps/spot/dev/"
machine = platform.uname().machine

# Lazy import of thicket - will be imported when needed
# import thicket as tt
import random

from .Reader import Reader


class TH_ens:

    th_ens_defined = 0
    th_ens = 0
    profiles = 0

    def get_th_ens(self, cali_files ):
        return self.get_th_ens_impl( cali_files )

    def get_th_ens_impl(self, cali_files):

        if TH_ens.th_ens_defined == 0:

            # Try to import thicket, adding common paths if needed
            try:
                import thicket as tt
            except ModuleNotFoundError:
                import sys
                # Try common thicket installation paths
                thicket_paths = [
                    "/Users/aschwanden1/thicket",
                    "/usr/gapps/spot/thicket",
                ]
                for path in thicket_paths:
                    if os.path.exists(path) and path not in sys.path:
                        sys.path.append(path)

                # Try importing again
                import thicket as tt

            TH_ens.th_ens_defined = 1

            # get a list of all cali files in subdirectory - recursively
            PATH = cali_files
            TH_ens.profiles = [
                y for x in os.walk(PATH) for y in glob(os.path.join(x[0], "*.cali"))
            ]

            #  this contains some metadata we need.
            #  also contains the tree data.
            # print( TH_ens.profiles )

            TH_ens.th_ens = tt.Thicket.from_caliperreader(TH_ens.profiles)

            # TH_ens.th_ens.dataframe.reset_index(drop=True, inplace=True)
            # TH_ens.th_ens.dataframe = pd.concat([TH_ens.th_ens.dataframe, TH_ens.th_ens.dataframe], ignore_index=True)

            # TH_ens.th_ens.metadata.reset_index(drop=True, inplace=True)
            # TH_ens.th_ens.metadata = pd.concat([TH_ens.th_ens.metadata, TH_ens.th_ens.metadata], ignore_index=True)
            # tms = ThicketMultiplierStub(TH_ens.th_ens)

        return TH_ens.th_ens, TH_ens.profiles


class ThicketReader(Reader):

    def __init__(self, th_ens, profiles, xaxis):
        self.th_ens = th_ens
        self.profiles = profiles
        self.xaxis = xaxis

    def get_x_axis(self):
        return self.xaxis

    def get_all_xaxis(self):

        xaxis_arr = []

        for profile, row in self.th_ens.metadata.iterrows():

            for xaxis, value in row.items():
                if xaxis == self.xaxis:
                    xaxis_arr.append(value)

        return xaxis_arr

    def get_all_xaxis_meta(self):

        xaxis_arr = []

        for profile, row in self.th_ens.metadata.iterrows():

            meta_obj = {}
            for xaxis, value in row.items():
                meta_obj[xaxis] = value

            meta_obj["profile"] = profile
            xaxis_arr.append(meta_obj)

        return xaxis_arr

    def make_random_number( self ):
        base = 1565172972
        num = base + random.randint(0, 8000000)
        return str(num)

    def get_entire(self):

        # PSTUB
        from .GraphTraverseModel import GraphTraverseModel

        gtm = GraphTraverseModel(self.th_ens, self.profiles)
        childrenMap = gtm.getParentToChildMapping()
        parentMap = gtm.getChildToParentMapping()

        # Get all unique xaxis values (e.g., all unique launchdate values)
        xaxis_arr = self.get_all_xaxis()
        meta_arr = self.get_all_xaxis_meta()

        # Get data for each xaxis value
        # This returns a dict: {xaxis_value: [list of node data]}
        nodes_by_xaxis = {}
        meta_by_xaxis = {}
        for idx, xaxis in enumerate(xaxis_arr):
            nodes_by_xaxis[xaxis] = self.get_entire_for_xaxis(xaxis)
            meta_by_xaxis[xaxis] = meta_arr[idx]

        # Transform the data structure to match what TreeScapeModel expects
        # TreeScapeModel expects: {node_name: {"xaxis": [metadata1, metadata2, ...], "ydata": [data1, data2, ...]}}
        # We currently have: {xaxis_value: [{"name": node_name, "ydata": data, "xaxis": ordered_xaxis}]}

        nodes = {}

        # Build a mapping of node_name -> list of (xaxis_value, ydata) pairs
        for xaxis_value, node_list in nodes_by_xaxis.items():
            for node_data in node_list:
                node_name = node_data["name"]
                ydata = node_data["ydata"][0]
                # xaxis_value is the metadata for this run

                if node_name not in nodes:
                    nodes[node_name] = {"name": node_name, "xaxis": [], "ydata": []}

                meta_stub = {
                    "cali.caliper.version": "2.2.0-dev",
                    "cali.channel": "spot",
                    "user": "chavez35",
                    "launchdate": self.make_random_number(),
                    "executablepath": "/g/g90/johnson234/exe/STRIP_HEADER/toss17/impending4.8-3472",
                    "libraries": "/etc/fin/etc/home.jafd",
                    "cmdline": "[-active COM",
                    "cluster": "rockfiro",
                    "jobsize": "2",
                    "threads": "101",
                    "iterations": "11400000",
                    "problem_size": "85",
                    "num_regions": "11",
                    "region_cost": "5",
                    "region_balance": "1",
                    "elapsed_time": "184.0",
                    "figure_of_merit": "6560.0",
                    "spot.metrics": "avg#face.duration#inclusive#sum5345"
                }

                nodes[node_name]["xaxis"].append(meta_by_xaxis[xaxis_value])
                nodes[node_name]["ydata"].append(ydata)

        return {
            "nodes": nodes,
            "childrenMap": childrenMap,
            "parentMap": parentMap,
            "meta_globals": {
                "cali.caliper.version": "string",
                "cali.channel": "string",
                "user": "string",
                "launchdate": "int",
                "executablepath": "string",
                "libraries": "string",
                "cmdline": "string",
                "cluster": "string",
                "jobsize": "int",
                "threads": "int",
                "iterations": "int",
                "problem_size": "int",
                "num_regions": "int",
                "region_cost": "int",
                "region_balance": "int",
                "elapsed_time": "float",
                "figure_of_merit": "float"
            }
        }

    def get_entire_for_xaxis(self, xaxis_name):

        df = self.th_ens.dataframe.reset_index()
        metaobj_idx_by_profile = {}

        # Build a mapping from profile identifier to metadata row
        # In Thicket, the index of metadata corresponds to the profile
        for profile_idx, row in self.th_ens.metadata.iterrows():
            # Access each column in the row
            metaobj_idx_by_profile[profile_idx] = row
        sumArr = {}
        count = {}
        howmany = 0

        #  YAxis: Now let's get the actual duration values, like the average durations.
        for index, row in df.iterrows():
            # Accessing individual elements in the row
            # print("row====")
            # print(row)

            howmany += 1

            #print(repr(row))
            #print(row)
            #exit()
            avg_duration = row["Avg time/rank"]
            #avg = row["avg#inclusive#sum#time.duration"]
            name = row["name"]
            profile = row["profile"]

            if name not in sumArr:
                sumArr[name] = {}
                count[name] = {}

            # Check if profile exists in the mapping
            if profile not in metaobj_idx_by_profile:
                # Profile might be a file path or other identifier
                # Skip this row if we can't find the metadata
                continue

            # Access the metadata row for this profile, then get the xaxis value
            # self.xaxis is the column name (e.g., "launchdate")
            # xaxis_name is the specific value we're filtering for
            metadata_row = metaobj_idx_by_profile[profile]
            ldate = metadata_row[self.xaxis]

            #  make sure that "['asdfasdf']" is regarded as a string.
            ldate = str(ldate)

            if ldate.isnumeric():
                ldate = float(ldate)

            # Filter: only process rows that match the xaxis_name we're looking for
            # Convert xaxis_name to the same type for comparison
            xaxis_name_normalized = str(xaxis_name)
            if xaxis_name_normalized.isnumeric():
                xaxis_name_normalized = float(xaxis_name_normalized)

            if ldate != xaxis_name_normalized:
                continue

            if ldate in sumArr[name]:
                sumArr[name][ldate]["sum"] += avg_duration
                count[name][ldate] += 1

                if avg_duration < sumArr[name][ldate]["min"]:
                    sumArr[name][ldate]["min"] = avg_duration

                if avg_duration > sumArr[name][ldate]["max"]:
                    sumArr[name][ldate]["max"] = avg_duration
            else:
                sumArr[name][ldate] = {
                    "sum": avg_duration,
                    "min": 1000,
                    "max": 0,
                    "avg": 0,
                }

                count[name][ldate] = 0

        # uniq_date = len(sumArr["main"])
        # print("uniq_date=" + str(uniq_date))

        # print("howmany=" + str(howmany))
        #MyTimer("get_entire_for_xaxis - iterrows")

        renderDat = {}
        ldates = {}
        nameOfLinesToPlot = []

        # Convert the dictionary to a list of tuples (launchDate, data)

        for name, launchData in sumArr.items():
            launch_list = [
                (launchDate, data) for launchDate, data in launchData.items()
            ]
            sorted_launch_list = sorted(
                launch_list,
                key=lambda x: (float(x[0]) if isinstance(x[0], (int, float)) else x[0]),
            )

            renderDat[name] = [data for _, data in sorted_launch_list]
            ldates[name] = [launchDate for launchDate, _ in sorted_launch_list]
            nameOfLinesToPlot.append(name)

        entireNodes = []

        #  name is node_name: like 'main', 'lulesh_cycle'
        #  it's the plot's name at the top.
        for name in renderDat:

            ordered = self.order_strings(ldates[name])

            entireNodes.append(
                {"name": name, "ydata": renderDat[name], "xaxis": ordered}
            )

        #MyTimer("get_entire_for_xaxis - renderDat")

        return entireNodes

    def order_strings(self, unsor_arr):
        # Check if the array contains strings with numbers
        if all(isinstance(s, str) and s.replace(".", "").isdigit() for s in unsor_arr):
            # Order the strings in numerical order
            ordered_arr = sorted(unsor_arr, key=lambda x: float(x))
            return ordered_arr
        else:
            return unsor_arr

    def test(self):
        import thicket as tt

        PATH = "/Users/aschwanden1/lulesh_gen/"
        profiles = [
            y for x in os.walk(PATH) for y in glob(os.path.join(x[0], "*.cali"))
        ]

        th_ens = tt.Thicket.from_caliperreader(profiles)

        # Iterate through each row
        for index, row in th_ens.metadata.iterrows():
            # Access each column in the row
            print(f"Profile: {index}")
            print(f"Version: {row['cali.caliper.version']}")
            print(f"Channel: {row['cali.channel']}")
            print(f"launchdate: {row['launchdate']}")
            print(f"elapsed_time: {row['elapsed_time']}")
            print(f"User: {row['user']}")
            # ... (print other columns as needed)
            print("\n")
