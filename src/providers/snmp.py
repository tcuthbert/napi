#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author    : Thomas Cuthbert
import os, sys
from providers.provider import Provider
from config.config import Config

sys.path.append('../')


def _reverse_dict(d):
    ret = {}
    for key, val in d.items():
        if ret.has_key(val):
            ret[val].append(key)
        else:
            ret[val] = [key]
    return ret


def _parse_routes(routing_table):
    ret = {}
    for key, value in routing_table.items():
        ret[key] = {}
        routes = [i.split('.') for i in value]
        for index, route in enumerate(routes):
            subnet = ".".join(route[0:4])
            ret[key][subnet] = {
                "mask": ".".join(route[4:8]),
                "next_hop": ".".join(route[9:])
            }
    return ret

def _strip_oid_from_list(oids, strip):
    """Iterates through list of oids and strips snmp tree off index.
    Returns sorted list of indexes.
    Keyword Arguments:
    self   --
    oid    -- Regular numeric oid index
    strip  -- Value to be stripped off index
    """
    sorted_oids = []
    for index in oids:
         s = index[0].replace(strip, "")
         sorted_oids.append((s, index[1]))

    return sorted(sorted_oids)


def _get_snmp(oid, hostname, community):
    """SNMP Wrapper function. Returns tuple of oid, value
    Keyword Arguments:
    oid       -- 
    community -- 
    """
    from pysnmp.entity.rfc3413.oneliner import cmdgen


    cmd_gen = cmdgen.CommandGenerator()

    error_indication, error_status, error_index, var_bind = cmd_gen.getCmd(
        cmdgen.CommunityData(community),
        cmdgen.UdpTransportTarget((hostname, 161)),
        oid)

    if error_indication:
        print(error_indication)
    else:
        if error_status:
            print ('%s at %s' % (
                error_status.prettyPrint(),
                error_index and var_bind[int(error_index)-1] or '?')
            )
        else:
            for name, value in var_bind:
                return (name.prettyPrint(), value.prettyPrint())


def _walk_snmp(oid, hostname, community):
    """SNMP getNext generator method. Yields each index to caller.
    Keyword Arguments:
    oid       -- 
    community -- 
    """
    from pysnmp.entity.rfc3413.oneliner import cmdgen

    cmd_gen = cmdgen.CommandGenerator()

    error_indication, error_status, error_index, var_bind_table = cmd_gen.nextCmd(
        cmdgen.CommunityData(community),
        cmdgen.UdpTransportTarget((hostname, 161)),
        oid)

    if error_indication:
        print(error_indication)
    else:
        if error_status:
            print ('%s at %s' % (
                error_status.prettyPrint(),
                error_index and var_bind_table[int(error_index)-1] or '?')
            )
        else:
            for var_bind_row in var_bind_table:
                for name, val in var_bind_row:
                    yield name.prettyPrint(), val.prettyPrint()


class SNMP(Provider):
    """docstring"""
    def __init__(self, *args, **kwargs):
        "docstring"
        self.snmp_params = Config.config_section_map("SNMP_PARAMS")
        self.snmp_oids = Config.config_section_map("OIDS")
        super(SNMP, self).__init__(*args, **kwargs)

    def __resolve_community_string(self):
        if self._device.device_type == "core":
            return self.snmp_params["community_core"]
        else:
            return self.snmp_params["community_remote"]
    
    def walk_tree_from_oid(self, oid):
        """Walks SNMP tree from rooted at oid.
        Oid must exist in the netlib configuration file else an exception is raised.

        :type oid: string
        :param oid: An SNMP oid index
        """
        try:
            index = self.snmp_oids[oid]
        except KeyError as e:
            #TODO: Logging
            print "oid not present in config file"
            raise e

        return dict(_strip_oid_from_list(list(_walk_snmp(index, self._device.hostname, self.__resolve_community_string())), index + "."))

    def __get_ipcidrrouteifindex(self):
        """Get routing table for use by Layer 3 object.
        This method gets the ipcidrrouteifindex routing table.
        """
        return self.walk_tree_from_oid("ipcidrrouteifindex")

    def _build_layer3_prop_routing_table(self):
        "Build routing table from device"
        return _parse_routes(_reverse_dict(self.__get_ipcidrrouteifindex()))

    def _build_layer2_prop_cam_table(self):
        "Build cam table from device"
        return "ff-ff-ff-ff"

    def _build_device_prop_interfaces(self):
        intfs = self.__get_index("ifname")
        for key, val in intfs.items():
            # intfs[key] = [intfs[key], self.__get_index("ifdesc")[key], self.__get_index("ifspeed")[key]]
            intfs[key] = {
                "intf_name": intfs[key],
                "intf_desc": self.__get_index("ifdesc")[key],
                "intf_speed": self.__get_index("ifspeed")[key]
            }
        return intfs

    def _wrapper_layer3_device_prop_interfaces(self, func):
        res = func()
        res.update({
            "0": {"intf_name": "INTERNAL"}
         })
        for key, value in _reverse_dict(self.walk_tree_from_oid("ipaddressifindex")).items():
            res[key].update({"intf_ip": value.pop()})
        return res

    def __get_index(self, index):
        "Gather interfaces for upstream device."
        oid = self.snmp_oids[index]
        hostname  = self._device.hostname
        return dict(_strip_oid_from_list(list(_walk_snmp(oid, hostname, self.__resolve_community_string())), oid + "."))
