"""
Author: Shawn Anderson

Date  : 1/19/19

Brief : Store the Gene as a dictionary as provide a wrapper for accessing and modifying the gene with this class. The
goal is to separate out the messy dictionary functions from the gene as much as possible

Notes :

Copyright 2019 California Institute of Technology.  ALL RIGHTS RESERVED.
U.S. Government Sponsorship acknowledged.
"""
import random

import numpy as np
import uuid

from toga.genetic_algorithm.genetype import GeneType
from toga.genetic_algorithm.mutate.handle_type import mutate
from toga.utils import first


class Node(object):
    """
    Handles creating a tree structure of the original gene
    """

    def __init__(self, parent=None, children=None, **kwargs):
        # This nodes unique identifier
        self.uuid = uuid.uuid4().hex
        self.name = kwargs.get('key')  # for now have name match the key that's being stored here

        # Hierarchy properties
        self.parent = parent
        self.children = [] if not children else children

        # Node Properties
        self._is_leaf = self.is_leaf  # Does ths node have children
        self._is_root = self.is_root  # Does this node have a parent
        self._mutable_children = True  # Allow mutators to act on this nodes children
        self.allow_mutations = True  # Allow mutations on this node
        self.leaf_count = 0  # the amount of leaves below this node, calling root should give the total count
        self._to_dictionary = {}  # convert the tree structure back to dictionary
        self._leaves = []  # the leaf nodes below this node

        # Gene Properties
        self.key = kwargs.get('key')  # the corresponding key from the yml gene representation
        self.gene_type = kwargs.get('gene_type')  # if this contain a type that is defined if so treat it as a block
        self.range_config = kwargs.get('range_config')  # the ranges allowed for this Nodes properties
        self.combine_tree = kwargs.get('combine_tree')  # Store the tree representation of combine subtree
        self.static_value = False if not kwargs.get('static_value') else kwargs.get('static_value')

        # Stored values at this node
        self.mutator = kwargs.get('mutator')  # What mutator is being used
        self.mutator_params = kwargs.get('mutator_params')
        self.values = []  # From each individual that is selected collect its value at this key and append here

        # The value this node will have after mutation
        self.value = None

    @property
    def is_leaf(self):
        self._is_leaf = True if not self.children or len(self.children) < 1 else False
        return self._is_leaf

    @property
    def is_root(self):
        self._is_root = True if self.parent is None else False
        return self._is_root

    @property
    def mutable_children(self):
        return self._mutable_children

    @mutable_children.setter
    def mutable_children(self, mutable):
        self._mutable_children = mutable

    @property
    def to_dictionary(self):
        self.update_dictionary()
        return self._to_dictionary

    @property
    def leaves(self):
        self._leaves = self.get_leaf_nodes()
        return self._leaves

    def toggle_mutate_leaves(self):
        leaves = self.leaves
        leaves = [i for i in leaves if i.static_value is False and len(i.values) > 0]

        mutable_allowed_num = 0
        if self.mutator == 'partial':
            mutable_allowed_num = random.randint(1, len(leaves))
        if self.mutator == 'min':
            mutable_allowed_num = len(leaves) - 1

        if leaves:
            # this is to disable mutation, opposite of what mutator would imply
            leaf_nodes = np.random.choice(leaves, size=mutable_allowed_num, replace=False)
            for leaf in leaf_nodes:
                node = self.get_nested_child(leaf.uuid)
                node.allow_mutations = False

    def add_child(self, child: 'Node') -> None:
        self.children.append(child)
        self.is_leaf  # Side effect, will update is leaf anytime this is called

    def remove_child(self, child: 'Node'):
        self.children.remove(child.uuid)
        self.is_leaf  # Side effect, will update is leaf anytime this is called

    def get_child(self, key: str):
        return first(x for x in self.children if x.name == key)

    def get_nested_child(self, uuid=''):
        """
        Only match against uuid to guarantee a match, incase of same name. Have a getter give self to get uuid for this
        :param uuid:
        :return:
        """
        for child in self.children:
            if child.uuid == uuid:
                return child
            child.get_nested_child()

    def remove(self):
        if not self.parent:
            return False

        self.parent.remove_child(self)

    def mutate_subtree(self):
        """
        Walks the tree and runs the mutate function

        Call this from GeneTree
        :return: None
        """

        if not self.children:
            return

        for child in self.children:
            child.mutate()  # run mutate
            child.mutate_subtree()  # run on children

    def get_leaf_nodes(self):
        leaves = []

        for child in self.children:
            if child.is_leaf:
                leaves.append(child)
            child.get_leaf_nodes()
        return leaves

    def update_leaf_count(self):
        """
        Walk the tree and count any leaf nodes and add up all leaf nodes to non leaf nodes

        Values for example tree after running:
        a=7
            b=1
            c=3
                e=2
                    j=1
                    k=1
                f=1
            d=3
                g=1
                h=1
                i=1

        :return: count of leaf nodes below this node
        """
        if not self.children:
            self.leaf_count += 1

        for child in self.children:
            child.update_leaf_count()
            self.leaf_count += child.leaf_count

    def insert_param_ranges(self, config_dict: dict, combine_case=True):
        key = self.key
        if combine_case:
            key = key.split('_methodnum_')[0]
        config_dict = config_dict.get(key)

        for child in self.children:
            key = child.key
            if combine_case:
                key = key.split('_methodnum_')[0]
            item = config_dict.get(key)
            param_type = item.get('param_type')
            if param_type:
                gene_type = GeneType(param_type)
                # Fill out config values according to keys defined in gene type enum
                range_config_dict = {}
                for _ in gene_type.keys:
                    range_config_dict[_] = item[_]
            child.gene_type = gene_type
            child.range_config = range_config_dict

    def walk_update_mutator(self, mutator):
        self.mutator = mutator

        for child in self.children:
            child.walk_update_mutator(mutator)

    def walk_insert_values(self, node: 'Node'):
        """
        Walk only trees that match keys as self

        :param node:
        :return:
        """
        if node.key == self.key:
            for child in self.children:
                insert_node_child = node.get_child(child.key)
                if insert_node_child:
                    child.insert_value(insert_node_child.value)
                child.walk_insert_values(insert_node_child)

    def insert_value(self, value):
        self.values.append(value)

    def update_dictionary(self):
        """
        Walk through all child entries and return a tree
        Use this at root to get a whole tree of the entries
        a
            b
            c
                e
                    j
                    k
                f
            d
                g
                h
                i
        a - {"b": "", "c":{"e": {"j": "", "k", ""}, "f": ""}, "d": {"g": "", "h": "", "i": ""}}
        :return:
        """
        if not self.children:
            if self.value:
                self._to_dictionary = {self.key: self.value}
            return

        _dict = {}
        for child in self.children:
            child.update_dictionary()
            _dict = {**_dict, **child._to_dictionary}
        self._to_dictionary = {self.key: _dict}

    def mutate(self):
        if self.allow_mutations:
            out = mutate(self.gene_type,
                         self.range_config,
                         self.value,
                         self.values,
                         None,
                         self.mutator_params.get('type_probability'))
            self.value = out
        else:
            if self.values:
                self.value = self.values[0]

        self._to_dictionary = {self.key: self.value}
