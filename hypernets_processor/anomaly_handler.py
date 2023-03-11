"""
AnomalyHandler class
"""

from hypernets_processor.version import __version__
from hypernets_processor.data_io.format.anomalies import ANOMALIES_DICT
from hypernets_processor.data_io.hypernets_db_builder import open_database


"""___Authorship___"""
__author__ = "Sam Hunt"
__created__ = "24/7/2020"
__version__ = __version__
__maintainer__ = "Sam Hunt"
__email__ = "sam.hunt@npl.co.uk"
__status__ = "Development"


class AnomalyHandler:
    """
    Class for handling anomalies

    :type context: hypernets_processor.context.Context
    :param context: processor context

    :type anomaly_db: hypernets_processor.data_io.hypernets_db_builder.AnomalyDB
    :param anomaly_db: (optional) anomaly database

    :type anomalies_dict: dict
    :param anomalies_dict: anomaly definitions (default defined in hypernets_processor.data_io.format.anomalies)
    """

    def __init__(
        self, context, anomaly_db=None, url=None, anomalies_dict=ANOMALIES_DICT
    ):
        self.context = context
        self.anomaly_db = None

        if anomaly_db is not None:
            self.anomaly_db = anomaly_db
        elif url is not None:
            self.anomaly_db = open_database(url, db_format="anomaly", context=context)

        self.anomalies_dict = anomalies_dict
        self.anomalies_added = []

    def add_anomaly(self, anomaly_id, ds=None):
        """
        Adds anomaly to anomaly database

        :type anomaly_id: str
        :param anomaly_id: anomaly id, must match name of entry in self.anomalies dict
        :type ds: xarray.Dataset
        :param ds: producgt that was being processed when anomaly was raised
        """

        # Check anomaly defined
        if anomaly_id not in self.get_anomaly_ids():
            self.context.logger.debug(
                "Unknown anomaly_id (" + anomaly_id + ") - not add to anomaly database"
            )
            return

        # Add anomaly to list of anomalies added during current processing
        self.anomalies_added.append(anomaly_id)

        # Add anomaly to db
        if self.anomaly_db is not None:
            self.anomaly_db.add_anomaly(anomaly_id,ds)

        # Exit if anomaly requires error
        error = self.get_anomaly_error(anomaly_id)
        error_msg = self.get_anomaly_error_msg(anomaly_id)
        if error is not None:
            self.context.logger.error(error_msg)
            print(error_msg)
            raise error(error_msg)

    def add_x_anomaly(self):
        """
        Adds unexpect error anomaly to anomaly database if expected anomaly not already
        """

        if self.get_sequence_crashing_anomalies() == []:
            self.add_anomaly("x")

    def get_anomaly_ids(self):
        """
        Returns available anomaly ids

        :rtype: list
        :return: anomaly ids
        """

        return list(self.anomalies_dict.keys())

    def get_anomaly_error(self, anomaly_id):
        """
        Returns error for anomaly id

        :rtype: Error
        :return: anomaly error
        """

        return self.anomalies_dict[anomaly_id]["error"]

    def get_anomaly_error_msg(self, anomaly_id):
        """
        Returns error msg for anomaly id

        :rtype: list
        :return: anomaly error msg
        """

        return self.anomalies_dict[anomaly_id]["error_msg"]

    def get_crashing_anomaly_ids(self):
        """
        Returns available anomaly ids that result in crashes

        :rtype: list
        :return: crashing anomaly ids
        """

        crashing_anomalies = []

        for anomaly_id in self.get_anomaly_ids():
            if self.get_anomaly_error(anomaly_id) is not None:
                crashing_anomalies.append(anomaly_id)

        return crashing_anomalies

    def get_sequence_anomalies(self, sequence_name=None, site_id=None):
        """
        Returns anomaly ids of anomalies currently registered for the processed sequence if context attribute is not
        None, else define of interest

        :type sequence_name: str
        :param sequence_name: (optional) name of sequence to lookup anomaly ids for, if omitted gets sequence id from
        context, if avaiable

        :type site_id: str
        :param site_id: (optional) name of site to lookup anomaly ids for, if omitted gets site id from
        context, if avaiable

        :rtype: list
        :return: sequence anomaly ids
        """

        # If anomaly_db available check anomaly_db
        # This is more robust, as it is valid for use even when not currently processing sequence
        if self.anomaly_db is not None:
            return self.anomaly_db.get_sequence_anomalies(sequence_name, site_id)

        # Otherwise get anomaly_ids added during current processing
        return self.anomalies_added

    def get_sequence_crashing_anomalies(self, sequence_name=None, site_id=None):
        """
        Returns crashing anomaly ids of anomalies currently registered for the processed sequence if context attribute
        is not None, else define

        :type sequence_name: str
        :param sequence_name: (optional) name of sequence to lookup anomaly ids for, if omitted gets sequence id from
        context, if avaiable

        :type site_id: str
        :param site_id: (optional) name of site to lookup anomaly ids for, if omitted gets site id from
        context, if avaiable

        :rtype: list
        :return: sequence crashing anomaly ids
        """

        if self.context is not None:
            sequence_name = self.context.get_config_value("sequence_name")
            site_id = self.context.get_config_value("site_id")

        crashing_sequence_anomalies = []
        for anomaly_id in self.get_sequence_anomalies(sequence_name, site_id):
            if anomaly_id in self.get_crashing_anomaly_ids():
                crashing_sequence_anomalies.append(anomaly_id)

        return crashing_sequence_anomalies


if __name__ == "__main__":
    pass
