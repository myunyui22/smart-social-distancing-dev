#!/usr/bin/python3
import logging
import configparser
import threading
from libs.notifications.slack_notifications import is_slack_configured
from libs.utils.mailing import is_mailing_configured


class ConfigEngine:
    """
    Handle the .ini confige file and provide a convenient interface to read the parameters from config.
    When an instance of ConfigeEngine is created you can use/pass it to other classes/modules that needs
    access to the parameters at config file.

    :param config_path: the path of config file
    """

    def __init__(self, config_path="./config-jetson-nano.ini"):
        self.logger = logging.getLogger(__name__)
        self.config = configparser.ConfigParser()
        self.config.optionxform = str
        self.config_file_path = config_path
        self.lock = threading.Lock()
        # For dynamic and cross-chapter flexible parameters:
        self.config._interpolation = configparser.ExtendedInterpolation()
        self.section_options_dict = {}
        self._load()

    def set_config_file(self, path):
        self.lock.acquire()
        try:
            self.config.clear()
            self.config_file_path = path
            self._load()
        finally:
            self.lock.release()

    def _load(self):
        self.config = configparser.ConfigParser()
        self.config.optionxform = str
        self.config.read(self.config_file_path)
        for section in self.config.sections():
            self.section_options_dict[section] = {}
            options = self.config.options(section)
            for option in options:
                try:
                    val = self.config.get(section, option)
                    self.section_options_dict[section][option] = val
                    if val == -1:
                        print("skip: %s" % option)
                except Exception:
                    print("exception on %s!" % option)
                    self.section_options_dict[section][option] = None

    def reload(self):
        self.lock.acquire()
        try:
            self._load()
        finally:
            self.lock.release()

    def save(self, path):
        self.lock.acquire()
        try:
            file_obj = open(path, "w")
            self.config.write(file_obj)
            file_obj.close()
        finally:
            self.lock.release()

    def get_section_dict(self, section):
        section_dict = None
        self.lock.acquire()
        try:
            section_dict = self.section_options_dict[section]
        finally:
            self.lock.release()
        return section_dict

    def get_sections(self):
        self.lock.acquire()
        sections = None
        try:
            sections = self.config.sections()
        finally:
            self.lock.release()
        return sections

    def get_boolean(self, section, option):
        result = None
        self.lock.acquire()
        try:
            result = self.config.getboolean(section, option)
        finally:
            self.lock.release()
        return result

    def toggle_boolean(self, section, option):
        self.lock.acquire()
        try:
            val = self.config.getboolean(section, option)
            self.config.set(section, option, str(not val))
        finally:
            self.lock.release()
        self.save(self.config_file_path)

    def set_option_in_section(self, section, option, value):
        self.lock.acquire()
        try:
            if self.config.has_section(section):
                self.config.set(section, option, value)
            else:
                self.config.add_section(section)
                self.config.set(section, option, value)
        finally:
            self.lock.release()

    """
    Receives a dictionary with the sections of the config and options to be updated.
    Saves the new config in the .ini file
    """

    def update_config(self, config, save_file=True):
        current_sections = []
        for section, options in config.items():
            if section.startswith(("Source", "Area", "PeriodicTask")):
                current_sections.append(section)
            for option, value in options.items():
                self.set_option_in_section(section, option, value)
        for section in self.config.sections():
            if (len(current_sections) and section.startswith(("Source", "Area", "PeriodicTask"))
                    and section not in current_sections):
                self.config.remove_section(section)
        self.set_option_in_section("App", "HasBeenConfigured", "True")
        if save_file:
            self.save(self.config_file_path)

    def get_entity_with_notifications(self, title, section):
        ent = {"section": title, "id": section["Id"], "name": section["Name"]}
        if "Tags" in section and section["Tags"].strip() != "":
            ent["tags"] = section["Tags"].split(",")
        if "Emails" in section and section["Emails"].strip() != "":
            ent["emails"] = section["Emails"].split(",")
        ent["enable_slack_notifications"] = self.config.getboolean(title, "EnableSlackNotifications")
        ent["notify_every_minutes"] = int(section["NotifyEveryMinutes"])
        ent["violation_threshold"] = int(section["ViolationThreshold"])
        ent["daily_report"] = self.config.getboolean(title, "DailyReport")
        ent["daily_report_time"] = section.get("DailyReportTime") or "06:00"

        return ent

    def get_video_sources(self):
        try:
            sources = []
            for title, section in self.config.items():
                if title.startswith("Source_"):
                    src = self.get_entity_with_notifications(title, section)
                    src["type"] = "Camera"
                    src["url"] = section["VideoPath"]
                    src["dist_method"] = section["DistMethod"]
                    if "Tags" in section and section["Tags"].strip() != "":
                        src["tags"] = section["Tags"].split(",")
                    if src["notify_every_minutes"] > 0 and src["violation_threshold"] > 0:
                        src["should_send_email_notifications"] = self.should_send_email_notifications(src)
                        src["should_send_slack_notifications"] = self.should_send_slack_notifications(src)
                    else:
                        src["should_send_email_notifications"] = False
                        src["should_send_slack_notifications"] = False
                    sources.append(src)
            return sources
        except Exception:
            # Sources are invalid in config file. What should we do?
            raise RuntimeError("Invalid sources in config file")

    def get_areas(self):
        try:
            areas = []
            for title, section in self.config.items():
                if title.startswith("Area_"):
                    area = self.get_entity_with_notifications(title, section)
                    area["type"] = "Area"
                    area["occupancy_threshold"] = int(section["OccupancyThreshold"])
                    if "Cameras" in section and section["Cameras"].strip() != "":
                        area["cameras"] = section["Cameras"].split(",")

                    if (area["notify_every_minutes"] > 0 and area["violation_threshold"] > 0) or area["occupancy_threshold"] > 0:
                        area["should_send_email_notifications"] = self.should_send_email_notifications(area)
                        area["should_send_slack_notifications"] = self.should_send_slack_notifications(area)
                    else:
                        area["should_send_email_notifications"] = False
                        area["should_send_slack_notifications"] = False
                    areas.append(area)
            return areas
        except Exception:
            # Sources are invalid in config file. What should we do?
            raise RuntimeError("Invalid areas in config file")

    def should_send_email_notifications(self, entity):
        if "emails" in entity:
            if is_mailing_configured():
                return True
            else:
                self.logger.warning("Tried to enable email notifications but oauth2_cred.json is missing")
        return False

    def should_send_slack_notifications(self, ent):
        if self.config["App"]["SlackChannel"] and ent["enable_slack_notifications"]:
            if is_slack_configured():
                return True
            else:
                self.logger.warning("Tried to enable slack notifications but slack_token.txt is either missing or unauthorized")
        return False
