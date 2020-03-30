from cloudshell.shell.core.driver_context import ResourceCommandContext, AutoLoadDetails, AutoLoadAttribute, \
    AutoLoadResource
from collections import defaultdict


class LegacyUtils(object):
    def __init__(self):
        self._datamodel_clss_dict = self.__generate_datamodel_classes_dict()

    def migrate_autoload_details(self, autoload_details, context):
        model_name = context.resource.model
        root_name = context.resource.name
        root = self.__create_resource_from_datamodel(model_name, root_name)
        attributes = self.__create_attributes_dict(autoload_details.attributes)
        self.__attach_attributes_to_resource(attributes, '', root)
        self.__build_sub_resoruces_hierarchy(root, autoload_details.resources, attributes)
        return root

    def __create_resource_from_datamodel(self, model_name, res_name):
        return self._datamodel_clss_dict[model_name](res_name)

    def __create_attributes_dict(self, attributes_lst):
        d = defaultdict(list)
        for attribute in attributes_lst:
            d[attribute.relative_address].append(attribute)
        return d

    def __build_sub_resoruces_hierarchy(self, root, sub_resources, attributes):
        d = defaultdict(list)
        for resource in sub_resources:
            splitted = resource.relative_address.split('/')
            parent = '' if len(splitted) == 1 else resource.relative_address.rsplit('/', 1)[0]
            rank = len(splitted)
            d[rank].append((parent, resource))

        self.__set_models_hierarchy_recursively(d, 1, root, '', attributes)

    def __set_models_hierarchy_recursively(self, dict, rank, manipulated_resource, resource_relative_addr, attributes):
        if rank not in dict: # validate if key exists
            pass

        for (parent, resource) in dict[rank]:
            if parent == resource_relative_addr:
                sub_resource = self.__create_resource_from_datamodel(
                    resource.model.replace(' ', ''),
                    resource.name)
                self.__attach_attributes_to_resource(attributes, resource.relative_address, sub_resource)
                manipulated_resource.add_sub_resource(
                    self.__slice_parent_from_relative_path(parent, resource.relative_address), sub_resource)
                self.__set_models_hierarchy_recursively(
                    dict,
                    rank + 1,
                    sub_resource,
                    resource.relative_address,
                    attributes)

    def __attach_attributes_to_resource(self, attributes, curr_relative_addr, resource):
        for attribute in attributes[curr_relative_addr]:
            setattr(resource, attribute.attribute_name.lower().replace(' ', '_'), attribute.attribute_value)
        del attributes[curr_relative_addr]

    def __slice_parent_from_relative_path(self, parent, relative_addr):
        if parent is '':
            return relative_addr
        return relative_addr[len(parent) + 1:] # + 1 because we want to remove the seperator also

    def __generate_datamodel_classes_dict(self):
        return dict(self.__collect_generated_classes())

    def __collect_generated_classes(self):
        import sys, inspect
        return inspect.getmembers(sys.modules[__name__], inspect.isclass)


class ReportingService(object):
    def __init__(self, name):
        """
        
        """
        self.attributes = {}
        self.resources = {}
        self._cloudshell_model_name = 'Reporting Service'
        self._name = name

    def add_sub_resource(self, relative_path, sub_resource):
        self.resources[relative_path] = sub_resource

    @classmethod
    def create_from_context(cls, context):
        """
        Creates an instance of NXOS by given context
        :param context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return:
        :rtype ReportingService
        """
        result = ReportingService(name=context.resource.name)
        for attr in context.resource.attributes:
            result.attributes[attr] = context.resource.attributes[attr]
        return result

    def create_autoload_details(self, relative_path=''):
        """
        :param relative_path:
        :type relative_path: str
        :return
        """
        resources = [AutoLoadResource(model=self.resources[r].cloudshell_model_name,
            name=self.resources[r].name,
            relative_address=self._get_relative_path(r, relative_path))
            for r in self.resources]
        attributes = [AutoLoadAttribute(relative_path, a, self.attributes[a]) for a in self.attributes]
        autoload_details = AutoLoadDetails(resources, attributes)
        for r in self.resources:
            curr_path = relative_path + '/' + r if relative_path else r
            curr_auto_load_details = self.resources[r].create_autoload_details(curr_path)
            autoload_details = self._merge_autoload_details(autoload_details, curr_auto_load_details)
        return autoload_details

    def _get_relative_path(self, child_path, parent_path):
        """
        Combines relative path
        :param child_path: Path of a model within it parent model, i.e 1
        :type child_path: str
        :param parent_path: Full path of parent model, i.e 1/1. Might be empty for root model
        :type parent_path: str
        :return: Combined path
        :rtype str
        """
        return parent_path + '/' + child_path if parent_path else child_path

    @staticmethod
    def _merge_autoload_details(autoload_details1, autoload_details2):
        """
        Merges two instances of AutoLoadDetails into the first one
        :param autoload_details1:
        :type autoload_details1: AutoLoadDetails
        :param autoload_details2:
        :type autoload_details2: AutoLoadDetails
        :return:
        :rtype AutoLoadDetails
        """
        for attribute in autoload_details2.attributes:
            autoload_details1.attributes.append(attribute)
        for resource in autoload_details2.resources:
            autoload_details1.resources.append(resource)
        return autoload_details1

    @property
    def cloudshell_model_name(self):
        """
        Returns the name of the Cloudshell model
        :return:
        """
        return 'ReportingService'

    @property
    def current_job_id(self):
        """
        :rtype: str
        """
        return self.attributes['Reporting Service.Current Job Id'] if 'Reporting Service.Current Job Id' in self.attributes else None

    @current_job_id.setter
    def current_job_id(self, value):
        """
        current job running against this sandbox
        :type value: str
        """
        self.attributes['Reporting Service.Current Job Id'] = value

    @property
    def smtp_resource(self):
        """
        :rtype: str
        """
        return self.attributes['Reporting Service.SMTP Resource'] if 'Reporting Service.SMTP Resource' in self.attributes else None

    @smtp_resource.setter
    def smtp_resource(self, value='admin smtp'):
        """
        name of cloudshell smtp resource which will send the mail
        :type value: str
        """
        self.attributes['Reporting Service.SMTP Resource'] = value

    @property
    def cs_https(self):
        """
        :rtype: bool
        """
        return self.attributes['Reporting Service.CS Https'] if 'Reporting Service.CS Https' in self.attributes else None

    @cs_https.setter
    def cs_https(self, value=False):
        """
        is cloudshell portal configured with ssl? this is for sending out correct links to sandbox
        :type value: bool
        """
        self.attributes['Reporting Service.CS Https'] = value

    @property
    def additional_recipients(self):
        """
        :rtype: str
        """
        return self.attributes['Reporting Service.Additional Recipients'] if 'Reporting Service.Additional Recipients' in self.attributes else None

    @additional_recipients.setter
    def additional_recipients(self, value):
        """
        comma separated list of email addresses, appended to sandbox owner mail
        :type value: str
        """
        self.attributes['Reporting Service.Additional Recipients'] = value

    @property
    def cc_recipients(self):
        """
        :rtype: str
        """
        return self.attributes['Reporting Service.Cc Recipients'] if 'Reporting Service.Cc Recipients' in self.attributes else None

    @cc_recipients.setter
    def cc_recipients(self, value):
        """
        comma separated list of email addresses to add to Cc
        :type value: str
        """
        self.attributes['Reporting Service.Cc Recipients'] = value

    @property
    def error_report_all(self):
        """
        :rtype: bool
        """
        return self.attributes['Reporting Service.Error Report All'] if 'Reporting Service.Error Report All' in self.attributes else None

    @error_report_all.setter
    def error_report_all(self, value=True):
        """
        to send email report to everybody, or just sandbox owner
        :type value: bool
        """
        self.attributes['Reporting Service.Error Report All'] = value

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        
        :type value: str
        """
        self._name = value

    @property
    def cloudshell_model_name(self):
        """
        :rtype: str
        """
        return self._cloudshell_model_name

    @cloudshell_model_name.setter
    def cloudshell_model_name(self, value):
        """
        
        :type value: str
        """
        self._cloudshell_model_name = value



