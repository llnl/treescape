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

import thicket as tt

from .Reader import Reader


class TH_ens:

    th_ens_defined = 0
    th_ens = 0
    profiles = 0

    def get_th_ens(self, cali_files ):
        return self.get_th_ens_impl( cali_files )

    def get_th_ens_impl(self, cali_files):

        if TH_ens.th_ens_defined == 0:

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

            for xaxis, row in row.items():
                if xaxis == self.xaxis:
                    xaxis_arr.append(xaxis)

            return xaxis_arr

    def get_entire(self):

        # PSTUB
        from GraphTraverseModel import GraphTraverseModel

        gtm = GraphTraverseModel(self.th_ens, self.profiles)
        # childrenMap = {'main': ['lulesh.cycle'], 'lulesh.cycle': ['TimeIncrement', 'LagrangeLeapFrog'], 'LagrangeLeapFrog': ['LagrangeNodal', 'LagrangeElements', 'CalcTimeConstraintsForElems'], 'CalcTimeConstraintsForElems': [], 'LagrangeElements': ['CalcLagrangeElements', 'CalcQForElems', 'ApplyMaterialPropertiesForElems'], 'ApplyMaterialPropertiesForElems': ['EvalEOSForElems'], 'EvalEOSForElems': ['CalcEnergyForElems'], 'CalcEnergyForElems': [], 'CalcLagrangeElements': ['CalcKinematicsForElems'], 'CalcKinematicsForElems': [], 'CalcQForElems': ['CalcMonotonicQForElems'], 'CalcMonotonicQForElems': [], 'LagrangeNodal': ['CalcForceForNodes'], 'CalcForceForNodes': ['CalcVolumeForceForElems'], 'CalcVolumeForceForElems': ['IntegrateStressForElems', 'CalcHourglassControlForElems'], 'CalcHourglassControlForElems': ['CalcFBHourglassForceForElems'], 'CalcFBHourglassForceForElems': [], 'IntegrateStressForElems': [], 'TimeIncrement': []}
        childrenMap = gtm.getParentToChildMapping()
        # parentMap = {'lulesh.cycle': 'main', 'TimeIncrement': 'lulesh.cycle', 'LagrangeLeapFrog': 'lulesh.cycle', 'LagrangeNodal': 'LagrangeLeapFrog', 'LagrangeElements': 'LagrangeLeapFrog', 'CalcTimeConstraintsForElems': 'LagrangeLeapFrog', 'CalcLagrangeElements': 'LagrangeElements', 'CalcQForElems': 'LagrangeElements', 'ApplyMaterialPropertiesForElems': 'LagrangeElements', 'EvalEOSForElems': 'ApplyMaterialPropertiesForElems', 'CalcEnergyForElems': 'EvalEOSForElems', 'CalcKinematicsForElems': 'CalcLagrangeElements', 'CalcMonotonicQForElems': 'CalcQForElems', 'CalcForceForNodes': 'LagrangeNodal', 'CalcVolumeForceForElems': 'CalcForceForNodes', 'IntegrateStressForElems': 'CalcVolumeForceForElems', 'CalcHourglassControlForElems': 'CalcVolumeForceForElems', 'CalcFBHourglassForceForElems': 'CalcHourglassControlForElems'}
        parentMap = gtm.getChildToParentMapping()

        # print(childrenMap)
        # print(parentMap)

        xaxis_arr = self.get_all_xaxis()
        nodes = {}

        for xaxis in xaxis_arr:
            nodes[xaxis] = self.get_entire_for_xaxis(xaxis)

        return {
            "nodes": nodes,
            "childrenMap": childrenMap,
            "parentMap": parentMap,
            "meta_globals": {}
        }

    def get_entire_for_xaxis(self, xaxis_name):

        df = self.th_ens.dataframe.reset_index()
        metaobj_idx_by_profile = {}

        for profile, row in self.th_ens.metadata.iterrows():
            # Access each column in the row
            metaobj_idx_by_profile[profile] = row

        # print(metaobj_idx_by_profile)
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

            ldate = metaobj_idx_by_profile[profile][xaxis_name]

            #  make sure that "['asdfasdf']" is regarded as a string.
            ldate = str(ldate)

            if ldate.isnumeric():
                ldate = float(ldate)

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

        uniq_date = len(sumArr["main"])
        print("uniq_date=" + str(uniq_date))

        print("howmany=" + str(howmany))
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
