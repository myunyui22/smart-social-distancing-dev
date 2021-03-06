import os
import logging

from datetime import date, timedelta

from libs.config_engine import ConfigEngine
from libs.metrics import FaceMaskUsageMetric, OccupancyMetric, SocialDistancingMetric
from libs.uploaders.s3_uploader import S3Uploader
from libs.utils.loggers import get_area_log_directory, get_source_log_directory

logger = logging.getLogger(__name__)


def raw_data_backup(config: ConfigEngine, bucket_name: str):
    """
    Uploads into S3 the raw data generated by the cameras and the areas.
    """
    s3_uploader = S3Uploader()
    sources = config.get_video_sources()
    areas = config.get_areas()
    source_log_directory = get_source_log_directory(config)
    area_log_directory = get_area_log_directory(config)
    # Backup all the source files
    for src in sources:
        source_directory = os.path.join(source_log_directory, src["id"])
        objects_log_directory = os.path.join(source_directory, "objects_log")
        today_objects_csv = os.path.join(objects_log_directory, str(date.today()) + ".csv")
        bucket_prefix = f"sources/{src['id']}/object_logs"
        if os.path.isfile(today_objects_csv):
            # Upload the today object files to S3
            s3_uploader.upload_file(bucket_name, today_objects_csv, f"{str(date.today())}.csv", bucket_prefix)
            #logger.info(f">>>>>>>>>>upload the today sources csv files to s3 in libs/backups/s3_backup.py\n")
    # Backup all the area files
    for area in areas:
        area_directory = os.path.join(area_log_directory, area["id"])
        occupancy_log_directory = os.path.join(area_directory, "occupancy_log")
        today_occupancy_csv = os.path.join(occupancy_log_directory, str(date.today()) + ".csv")
        bucket_prefix = f"areas/{area['id']}/occupancy_log"
        if os.path.isfile(today_objects_csv):
            # Upload the today occupancy files to S3
            s3_uploader.upload_file(bucket_name, today_occupancy_csv, f"{str(date.today())}.csv", bucket_prefix)
            #logger.info(f">>>>>>>>>>upload the today areas csv files to s3")


def reports_backup(config: ConfigEngine, bucket_name: str):
    """
    Uploads into s3 the reports generated yesterday by the cameras and the areas.
    """
    s3_uploader = S3Uploader()
    sources = config.get_video_sources()
    areas = config.get_areas()
    source_log_directory = get_source_log_directory(config)
    area_log_directory = get_area_log_directory(config)
    yesterday = str(date.today() - timedelta(days=1))
    # Backup the sources yesterday reports
    for src in sources:
        source_directory = os.path.join(source_log_directory, src["id"])
        reports_directory = os.path.join(source_directory, "reports")
        source_metrics = [FaceMaskUsageMetric, SocialDistancingMetric]
        for metric in source_metrics:
            metric_folder = os.path.join(reports_directory, metric.reports_folder)
            metric_hourly_report = os.path.join(metric_folder, f"report_{yesterday}.csv")
            metric_daily_report = os.path.join(metric_folder, "report.csv")
            bucket_prefix = f"sources/{src['id']}/reports/{metric.reports_folder}"
            if os.path.isfile(metric_hourly_report):
                s3_uploader.upload_file(bucket_name, metric_hourly_report, f"report_{yesterday}.csv", bucket_prefix)
                #logger.info(f">>>>>>>>>>upload the yesterday metric_hourly_report report_{yesterday}.csv sources csv files to s3 in libs/backups/s3_backup.py\n")
            if os.path.isfile(metric_daily_report):
                s3_uploader.upload_file(bucket_name, metric_daily_report, "report.csv", bucket_prefix)
                #logger.info(f">>>>>>>>>>upload the yesterday metric_daily_report report sources csv files to s3 in libs/backups/s3_backup.py\n")
    # Backup the areas yesterday reports
    for area in areas:
        area_directory = os.path.join(area_log_directory, area["id"])
        occupancy_reports_directory = os.path.join(area_directory, "reports", OccupancyMetric.reports_folder)
        occupancy_hourly_report = os.path.join(occupancy_reports_directory, f"report_{yesterday}.csv")
        occupancy_daily_report = os.path.join(occupancy_reports_directory, "report.csv")
        bucket_prefix = f"areas/{area['id']}/reports/{OccupancyMetric.reports_folder}"
        if os.path.isfile(occupancy_hourly_report):
            s3_uploader.upload_file(bucket_name, occupancy_hourly_report, f"report_{yesterday}.csv", bucket_prefix)
            #logger.info(f">>>>>>>>>>upload the yesterday metric_hourly_report report_{yesterday}.csv areas csv files to s3 in libs/backups/s3_backup.py\n")
        if os.path.isfile(occupancy_daily_report):
            s3_uploader.upload_file(bucket_name, occupancy_hourly_report, "report.csv", bucket_prefix)
            #logger.info(f">>>>>>>>>>upload the yesterday report metric_daily_report areas csv files to s3 in libs/backups/s3_backup.py\n")
