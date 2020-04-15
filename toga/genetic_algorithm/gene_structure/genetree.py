"""
Author: Shawn Anderson

Date  : 12/19/19

Brief : Store the Gene as a dictionary as provide a wrapper for accessing and modifying the gene with this class. The
goal is to separate out the messy dictionary functions from the gene as much as possible

Notes :

Copyright 2019 California Institute of Technology.  ALL RIGHTS RESERVED.
U.S. Government Sponsorship acknowledged.
"""
from __future__ import annotations

from toga.genetic_algorithm.gene_structure.node import Node
from toga.genetic_algorithm.genetype import GeneType


class GeneTree(object):
    """

    """

    def __init__(self, config: dict, parents: [], mutator: str, mutator_params: dict):
        # Attributes needed to define a gene tree that can create specific values
        self.config = config  # the ranges allowed defined in the range file
        self.parents = parents  # the selected instances that will be used to create a new instance with
        self.mutator = {'mutator': mutator,  # the mutator that will be applied to the tree to output a new value
                        'mutator_params': mutator_params}  # extra values a particular mutator might require

        # create a tree based on the range config to map values from parents to here
        self.tree = self.create_tree()

    def create_tree(self, root=None):
        if not self.config:
            raise Exception("No range config was found to define how to work with gene files for TOGA")

        if not root:
            root = Node(None, children=None, **{'key': 'root'})

        # Walk with side effects, will use the range config dictionary to update the values of root
        self.update(self.config, node=root, mutator=self.mutator)

        root.update_leaf_count()

        # Update the Tree based on the parents values
        if not self.parents:
            return root

        for _ in self.parents:
            self.walk(gene_dict=_, config_dictionary=self.config, node=root)

        root.toggle_mutate_leaves()

        return root

    def walk(self, gene_dict: dict, config_dictionary: dict, node: 'Node'):
        """
        Walk the gene_dictionary and update nodes values with matching key, values

        :param gene_dict: the dictionary of the genetic algorithm parent being stored
        :param config_dictionary: the gene_range parameters being stored
        :param node: the tree that is being updated
        :return: None, with side effects on the node parameter
        """
        for key, item in gene_dict.items():
            if isinstance(item, dict):
                if '_methodnum_' in key:
                    key = key.split('_methodnum_')[0]
                config_item = config_dictionary.get(key)  # use the the same key as gene_dict to walk the config as well
                _type = config_item.get('param_type')  # check if the config has a param_type key at this location
                if _type is None:
                    node.get_child(key)
                    child = node.get_child(key)
                    if child:
                        child.values.append(item)
                        self.walk(item, config_item, child)
                else:
                    # gene type param
                    gene_type = GeneType(_type)

                    # Fill out config values according to keys defined in gene type enum
                    range_config_dict = {}
                    for _ in gene_type.keys:
                        range_config_dict[_] = config_item[_]

                    child = node.get_child(key)
                    child.values.append(item)
                    # walk with the inner dictionaries to see if child nodes need to be added to tree
                    self.walk(item, config_item, child)
            else:
                child = node.get_child(key)
                if child is not None:
                    child.values.append(item)

    def mutate(self):
        # mutate the tree and get as dictionary
        self.tree.mutate_subtree()
        return self.tree.to_dictionary.get('root')

    def update(self, _dict: dict, node: 'Node', mutator=None):
        for key, item in _dict.items():
            if isinstance(item, dict):
                param_type = item.get('param_type')
                if 'param_type' in item:

                    gene_type = GeneType(param_type)

                    # Fill out config values according to keys defined in gene type enum
                    range_config_dict = {}
                    for _ in gene_type.keys:
                        range_config_dict[_] = item[_]

                    child = Node(parent=node, children=None, **{'key': key,
                                                                'value': None,
                                                                'gene_type': gene_type,
                                                                'range_config': range_config_dict,
                                                                'mutator': mutator.get('mutator'),
                                                                'mutator_params': mutator.get('mutator_params')
                                                                })
                    node.add_child(child)
                else:
                    child = Node(parent=node, children=None, **{'key': key,
                                                                'mutator': mutator.get('mutator'),
                                                                'mutator_params': mutator.get('mutator_params')})
                    node.add_child(child)
                    self.update(item, child, mutator)
            else:
                child = Node(parent=Node, children=None, **{'key': key,
                                                            'mutator_params': mutator.get('mutator_params'),
                                                            'static_value': True})
                child.value = item
                node.add_child(child)
