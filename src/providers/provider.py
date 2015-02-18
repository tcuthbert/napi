#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author    : Thomas Cuthbert
import os, sys
sys.path.append('../')
from config.config import Config


class Provider(object):
    """docstring"""


    def __init__(self, dev, *args, **kwargs):
        "docstring"
        self._device = dev
        self._register_attr(self._gather_provider_methods())

    def _gather_provider_methods(self):
        "Gather methods that correctly apply to upstream Device object"
        members = [name for name in dir(self) if name.startswith('_build_')]
        ret = []
        for iii in xrange(len(members)):
            if Provider._match_method_to_device(str(type(self._device).__name__).lower(), members[iii]):
                prop = getattr(self, members[iii])
                ret.append(members[iii])
        return ret

    def _register_attr(self, attributes):
        "Dynamically register read-only properties to Device derived object."
        def property_compiler(prop_name):
            def property_getter(self):
                return getattr(self, "_" + prop_name)
            ret_func = property_getter
            ret_func.__name__ += prop_name
            return ret_func
        for attr in attributes:
            try:
                prop_name = Provider._chomp_meta_from_method(attr, "prop_")
                res = self._bind_wrapper(attr)
                setattr(self._device, "_" + prop_name, res) # Bind property to upstream Device.
                cl = type(self._device)
                setattr(cl, prop_name, property(property_compiler(prop_name))) # Bind getter method for property.
            except Exception as e:
                # TODO: LOGGING
                print "{0}".format(e)
                raise e
    
    @staticmethod
    def _match_wrapper_to_method(self, fn):
        tmp_fn = fn.split("_")
        tmp_fn[1] = "wrapper_%s" % str(type(self._device).__name__).lower()
        tmp_fn = "_".join(tmp_fn)
        for attr in dir(self):
            if attr == tmp_fn:
                return attr
        return
    
    @staticmethod
    def _match_method_to_device(obj, method_name):
        "Match method name to callee class name"
        method_name = method_name.split('_')[2]
        obj = obj.split('.')
        if method_name in obj[-1] or method_name == "device":
            return True

    @staticmethod
    def _chomp_meta_from_method(method_name, split_word):
        "Strip leading meta info from method name."
        # split_word = "prop_"
        index = str.index(method_name, split_word)
        return method_name[index + len(split_word):]


    def _bind_wrapper(self, function_name):
        "Wrap provider method call with Device class method."
        wrapper = Provider._match_wrapper_to_method(self, function_name)
        function = getattr(self, function_name)
        if wrapper:
            wrap = getattr(self, wrapper)
            return wrap(function)
        else:
            return function()
