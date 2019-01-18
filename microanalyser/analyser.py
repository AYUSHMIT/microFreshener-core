from .model.nodes import Service, Database, CommunicationPattern
from .model.relationships import InteractsWith
from .model.template import MicroModel

class MicroAnalyser(object):

    def __init__(self, micro_model):
        self.micro_model = micro_model
        self.wrong_cuts_relationships = []
        self.shared_databases = []
        self.not_independently_deployabe_services = []
        self.not_horizzontally_scalable_services = []
        self.not_fault_resilient_services = []

    def analyse(self):
        for node in self.micro_model.services:
            for relationship in node.relationships:
                if(self.is_wrong_cut(relationship)):
                    self.wrong_cuts_relationships.append(str(relationship))
        for node in self.micro_model.databases:
            if(self.is_shared_database(node)):
                self.shared_databases.append(str(node))
        for node in self.micro_model.services:
            if not self.is_independently_deployabe(node):
                self.not_independently_deployabe_services.append(str(node))
            if not self.is_horizzontally_scalable(node):
                self.not_horizzontally_scalable_services.append(str(node))
            if not self.is_fault_resilient(node):
                self.not_fault_resilient_services.append(str(node))
        return {'wrong_cuts_relationship': self.wrong_cuts_relationships,
                'shared_databases': self.shared_databases,
                'not_independently_deployable': self.not_independently_deployabe_services,
                'not_horizzontally_scalable_services': self.not_horizzontally_scalable_services,
                'not_fault_resilient_services': self.not_fault_resilient_services
                }

    def analyse_squad(self, name):
        wc_rels = {}
        squad = self.micro_model.get_squad(name)
        for member in squad.members:
           wc_rels[member.name] = self.analyse_node(member.name)
        return wc_rels

    def analyse_node(self, name):
        wrong_cuts_relationships = []
        node = self.micro_model[name]
        for relationship in node.relationships:
                if(self.is_wrong_cut(relationship)):
                    wrong_cuts_relationships.append(str(relationship))
        return  wrong_cuts_relationships

    def is_wrong_cut(self, relationship):
        source_node = relationship.source
        target_node = relationship.target
        source_squad = self.micro_model.squad_of(source_node)
        target_squad = self.micro_model.squad_of(target_node)
        if (isinstance(source_node, Service) and isinstance(target_node, Database)
            and source_squad != target_squad):
            return True
        return False

    def is_shared_database(self, node):
        s = set(rel for rel in node.incoming)
        return  len(s) > 1
        # if(len(s) > 1):
        #     return True
        # else:
        #     return False

    def is_independently_deployabe(self, node):
        interaction = [dt_interaction for dt_interaction in node.deployment_time
                       if (isinstance(dt_interaction.target, Service)
                           # TODO: cehck if is derived from a Communication Pattern
                           or isinstance(dt_interaction.target, CommunicationPattern))]
        if(interaction):
            return False
        else:
            return True

    def is_horizzontally_scalable(self, node):
        interactions = [up_rt for up_rt in node.up_run_time_requirements if (
            isinstance(up_rt.source, Service))]
        if(interactions):
            return False
        else:
            return True

    def is_fault_resilient(self, node):
        interactions = [rt_int for rt_int in node.run_time if isinstance(
            rt_int.target, Service)]
        # TODO: guardare se esiste un path che arriva a un'altro servizio in cui non c'è un CircuiBreaker
        # odes_patterns = [req.target for req in node.run_time if (isinstance(req.target, CommunicationPattern) and
        #                                              renq.target.concrete_type !=  CIRCUIT_BREAKER)
        #             ]
        # vs_patterns = [node for node in nodes_patterns if node.]
        if(interactions):
            return False
        else:
            return True

    # shared persitency antipattern
    def all_shared_databases(self):
        """Check the  presence of inapprorpiate service intimacy and shared persistency antipatterns"""
        shared_databases = []
        for node in self.micro_model.databases:
            if(self.is_shared_database(node)):
                shared_databases.append(str(node))
        return shared_databases

    def all_not_independently_deployabe(self):
        service_with_deployment_interactions = []
        for node in self.micro_model.services:
            if(not self.is_independently_deployabe(node)):
                service_with_deployment_interactions.append(str(node))
        return service_with_deployment_interactions

    def all_not_horizzontally_scalable(self):
        services_with_direct_run_time = []
        for node in self.micro_model.services:
            if(not self.is_horizzontally_scalable(node)):
                services_with_direct_run_time.append(str(node))
        return services_with_direct_run_time

    def all_not_fault_resilient(self):
        services_not_fault_resilient = []
        for node in self.micro_model.services:
            if(not self.is_fault_resilient(node)):
                services_not_fault_resilient.append(str(node))
        return services_not_fault_resilient
