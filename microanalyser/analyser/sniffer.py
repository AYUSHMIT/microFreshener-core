
from abc import ABCMeta, abstractmethod
from .smell import NodeSmell, SingleLayerTeamSmell, EndpointBasedServiceInteractionSmell, NoApiGatewaySmell, WobblyServiceInteractionSmell, SharedPersistencySmell
from ..model.nodes import Service, Database, CommunicationPattern
from ..model.type import MESSAGE_ROUTER
from ..model.template import MicroModel
from ..model.groups import Edge, Squad
from typing import List

from ..helper.decorator import visitor


class NodeSmellSniffer(metaclass=ABCMeta):

    @abstractmethod
    def snif(self, node)->NodeSmell:
        pass


class GroupSmellSniffer(metaclass=ABCMeta):

    def __init__(self, micromodel: MicroModel):
        self.micro_model = micromodel

    @abstractmethod
    def snif(self, group):
        pass


class EndpointBasedServiceInteractionSmellSniffer(NodeSmellSniffer):

    def __str__(self):
        return 'EndpointBasedServiceInteractionSniffer({})'.format(super(NodeSmellSniffer, self).__str__())

    @visitor(Service)
    def snif(self, node):
        smell = EndpointBasedServiceInteractionSmell(node)
        for up_rt in node.up_run_time_requirements:
            if(isinstance(up_rt.source, Service)) and up_rt.timeout == False:
                smell.addLinkCause(up_rt)
        return smell

    @visitor(MicroModel)
    def snif(self, micro_model):
        print("visiting all the nodes in the graph")


class WobblyServiceInteractionSmellSniffer(NodeSmellSniffer):

    def __str__(self):
        return 'WobblyServiceInteractionSmellSniffer({})'.format(super(NodeSmellSniffer, self).__str__())

    @visitor(Service)
    def snif(self, node):
        # TODO: check also if there is a path from the node to a service node without a circuit breaker
        smell = WobblyServiceInteractionSmell(node)
        for rt in node.run_time:
            if (isinstance(rt.target, Service) and not rt.timeout):
                smell.addLinkCause(rt)
        return smell

    @visitor(MicroModel)
    def snif(self, micro_model):
        print("visiting al lthe nodes in the graph")

class SharedPersistencySmellSniffer(NodeSmellSniffer):

    def __str__(self):
        return 'SharedPersistencySmellSniffer({})'.format(super(NodeSmellSniffer, self).__str__())

    @visitor(Database)
    def snif(self, node)->SharedPersistencySmell:
        smell = SharedPersistencySmell(node)
        if (len(node.incoming)>1):
            for link in node.incoming:
                smell.addLinkCause(link)
        return smell

    @visitor(MicroModel)
    def snif(self, micro_model):
        print("visiting all the nodes in the graph")


class NoApiGatewaySmellSniffer(GroupSmellSniffer):

    def __str__(self):
        return 'NoApiGatewaySmellSniffer({})'.format(super(GroupSmellSniffer, self).__str__())
    
    @visitor(Edge)
    def snif(self, group: Edge)->[NoApiGatewaySmell]:
        foundNoApiGatewaySmells = []
        for node in group.members:
            if not isinstance(node, CommunicationPattern) or (isinstance(node, CommunicationPattern)  and node.concrete_type != MESSAGE_ROUTER):
                smell = NoApiGatewaySmell(node)
                smell.addNodeCause(node)
                foundNoApiGatewaySmells.append(smell)
        return foundNoApiGatewaySmells

class SingleLayerTeamSmellSniffer(GroupSmellSniffer):

    def snif(self, group: Squad)->SingleLayerTeamSmell:
        smell = SingleLayerTeamSmell(group)
        for node in group.members:
            for relationship in node.relationships:
                source_node = relationship.source
                target_node = relationship.target
                source_squad = self.micro_model.squad_of(source_node)
                target_squad = self.micro_model.squad_of(target_node)
                if (isinstance(source_node, Service) and isinstance(target_node, Database)
                        and source_squad != target_squad):
                    smell.addLinkCause(relationship)
        return smell

    def __str__(self):
        return 'SingleLayerTeamSmellSniffer({})'.format(super(GroupSmellSniffer, self).__str__())
