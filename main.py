import os
import os.path
import json
import pathlib
from pathlib import Path
from gi.repository import Notify
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import (
    KeywordQueryEvent,
    ItemEnterEvent,
    PreferencesEvent,
    PreferencesUpdateEvent,
)
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction


class Utils:
    @staticmethod
    def get_path(filename):
        current_dir = pathlib.Path(__file__).parent.absolute()
        return f"{current_dir}/{filename}"


class Zoom:
    open_command_paths = ["/usr/bin/xdg-open", "usr/bin/open"]
    meetings = []

    def get_installed_path(self):
        for path in self.open_command_paths:
            if os.path.exists(path):
                return path
        return False

    def is_installed(self):
        return bool(self.installed_path)

    def get_meeting_uri(self, meeting_id, password):
        password_string = f"&pwd={password}" if password else ""
        return f"zoommtg://zoom.us/join?action=join&confno={meeting_id}{password_string}"

    def join_meeting(self, meeting_id, password):
        if not self.is_installed():
            return
        os.system(
            f"{self.installed_path} \"{self.get_meeting_uri(meeting_id, password)}\"")

    def __init__(self):
        self.installed_path = self.get_installed_path()


class ZoomExtension(Extension):
    keyword = None
    zoom = None

    def __init__(self):
        super(ZoomExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent,
                       PreferencesUpdateEventListener())
        self.zoom = Zoom()

    history_file_path = Path(Path(__file__).parent) / "meetings"

    def get_meeting_ext_result_items(self, query):

        query = query.lower() if query else ""
        items = []
        with self.history_file_path.open('r') as history_file:
            data = history_file.readlines()
            if len(data) == 0 or data[0] == "\n":
                return "empty"
            

            for meeting in data:
                data = meeting.split("#")
                if len(data) == 3:
                    password = data[2].rstrip()
                else:
                    password = False
                items.append(
                    ExtensionResultItem(
                        icon=Utils.get_path("images/icon.svg"),
                        name=data[0],
                        on_enter=ExtensionCustomAction(
                            {
                                "meeting_id": data[1],
                                "password": password,
                                "action": "run"
                            }
                        ),
                    )
                )
            return items

    def update_meeting_history(self, name, zoom_id, password):
        name = name.rstrip()
        zoom_id = zoom_id.rstrip()
        password = password.rstrip()

        with ZoomExtension.history_file_path.open('r') as history_file:
            data = history_file.readlines()
            data.append(str(name)+"#"+str(zoom_id)+"#"+str(password) + "\n")
            data.reverse()
        with ZoomExtension.history_file_path.open('w') as history_file:
            for element in data:
                history_file.write(element)

    zoom_id = None
    zoom_password = None
    zoom_name = None


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        items = []
        global zoom_id
        global zoom_password
        global zoom_name

        if not extension.zoom.is_installed():
            items.append(
                ExtensionResultItem(
                    icon=Utils.get_path("images/icon.svg"),
                    name="No Zoom?",
                    description="Can't find the Zoom, or `open` or `xdg-open` command in your system :(",
                    highlightable=False,
                    on_enter=HideWindowAction(),
                )
            )
            return RenderResultListAction(items)

        argument = event.get_argument() or ""

        if argument == "z":
            extension.update_meeting_history()

        if argument is None:
            return RenderResultListAction(None)
        if argument.startswith("join"):
            zoom_id = argument.replace("join ", "").rstrip()
            return RenderResultListAction([ExtensionResultItem(icon=Utils.get_path("images/icon.svg"),
                                                               name="Joining with ID: "+zoom_id, description="Enter meeting ID",
                                                               on_enter=SetUserQueryAction("zm password > "))])

        if argument.startswith("password >"):

            zoom_password = argument.replace("password > ", "").rstrip()
            return RenderResultListAction([ExtensionResultItem(icon=Utils.get_path("images/icon.svg"),
                                                               name="Joining with PWD: "+zoom_password, description="Enter password or keep blank",
                                                               on_enter=SetUserQueryAction("zm name > "))])
        if argument.startswith("name >"):
            zoom_name = argument.replace("name > ", "").rstrip()
            return RenderResultListAction([ExtensionResultItem(icon=Utils.get_path("images/icon.svg"),
                                                               name="Enter name: "+zoom_name, description="Enter meeting name",
                                                               on_enter=ExtensionCustomAction({"action": "insert", "name": zoom_name.rstrip(), "meeting_id": zoom_id.rstrip(), "password": zoom_password.rstrip()}))])
        if extension.get_meeting_ext_result_items(argument) == "empty":
            return RenderResultListAction([ExtensionResultItem(icon=Utils.get_path("images/icon.svg"),
                                                               name="No history results found",
                                                               on_enter=DoNothingAction())])

        else:
            items.extend(extension.get_meeting_ext_result_items(argument))
        return RenderResultListAction(items)


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        data = event.get_data()
        action = data["action"]
        if data["action"] == "insert":
            name = data["name"]
            meeting_id = data["meeting_id"]
            password = data["password"]
            extension.zoom.join_meeting(meeting_id, password)
            ZoomExtension.update_meeting_history(
                self, name, meeting_id, password)

        else:
            meeting_id = data["meeting_id"]
            password = data["password"]
            extension.zoom.join_meeting(meeting_id, password)


class PreferencesEventListener(EventListener):
    def on_event(self, event, extension):
        extension.keyword = event.preferences["zoom_kw"]


class PreferencesUpdateEventListener(EventListener):
    def on_event(self, event, extension):
        if event.id == "zoom_kw":
            extension.keyword = event.new_value


if __name__ == "__main__":
    ZoomExtension().run()
