from flask import Blueprint, jsonify, request
import oci
from oci.util import to_dict
from datetime import datetime, timedelta
import logging

bp = Blueprint('oracle_monitoring', __name__, url_prefix='/oracle/monitoring')

logging.basicConfig(level=logging.DEBUG)

@bp.route('/instances', methods=['GET'])
def list_instances():
    try:
        logging.debug("Listing instances...")
        config = oci.config.from_file("~/.oci/config")
        compute_client = oci.core.ComputeClient(config)
        instances = compute_client.list_instances(config['tenancy']).data
        instances_dict = [to_dict(instance) for instance in instances]
        logging.debug(f"Instances: {instances_dict}")
        return jsonify(instances_dict), 200
    except Exception as e:
        logging.error(f"Error listing instances: {str(e)}")
        return jsonify({'error': str(e)}), 400

@bp.route('/metrics', methods=['GET'])
def get_metrics():
    try:
        instance_id = request.args.get('instance_id')
        if not instance_id:
            logging.error("Instance ID not provided")
            return jsonify({'error': 'instance_id query parameter is required'}), 400

        logging.debug(f"Getting metrics for instance_id: {instance_id}")
        config = oci.config.from_file("~/.oci/config")
        monitoring_client = oci.monitoring.MonitoringClient(config)

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)

        logging.debug(f"Time range: {start_time} to {end_time}")
        response = monitoring_client.summarize_metrics_data(
            compartment_id=config['tenancy'],
            summarize_metrics_data_details=oci.monitoring.models.SummarizeMetricsDataDetails(
                namespace='oci_computeagent',
                query=f'CpuUtilization[1m].mean()',
                start_time=start_time.isoformat() + 'Z',
                end_time=end_time.isoformat() + 'Z'
            )
        )

        metrics_data = [to_dict(metric) for metric in response.data]
        logging.debug(f"Metrics data: {metrics_data}")
        return jsonify(metrics_data), 200
    except Exception as e:
        logging.error(f"Error getting metrics: {str(e)}")
        return jsonify({'error': str(e)}), 400
