import os
import os.path
import json
import pathlib
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
        os.system(f"{self.installed_path} \"{self.get_meeting_uri(meeting_id, password)}\"")

    def __init__(self):
        self.meetings = json.load(open(Utils.get_path("meetings.json"), "r"))
        self.installed_path = self.get_installed_path()


class ZoomExtension(Extension):
    keyword = None
    zoom = None

    def __init__(self):
        super(ZoomExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesUpdateEventListener())
        self.zoom = Zoom()

    def get_meeting_ext_result_items(self, query, open_with_id):
        items = []

        if open_with_id == "True":
            try:
                int(query)
            except Exception:
                pass
            else:
                items.append(
                    ExtensionResultItem(
                        icon=Utils.get_path("images/icon.svg"),
                        name=f"Open meeting with id: {query}",
                        on_enter=ExtensionCustomAction(
                            {
                                "meeting_id": query,
                                "password": False,
                            }
                        ),
                    )
                )

        query = query.lower() if query else ""
        data = list(
            filter(
                (
                    lambda c: any(
                        map(
                            lambda d: d.lower().startswith(query),
                            c.values(),
                        )
                    )
                ),
                self.zoom.meetings,
            )
        )
        for meeting in data[0:10]:
            items.append(
                ExtensionResultItem(
                    icon=Utils.get_path("images/icon.svg"),
                    name=meeting["name"],
                    on_enter=ExtensionCustomAction(
                        {
                            "meeting_id": meeting["id"],
                            "password": meeting["pwd"] if "pwd" in meeting else False,
                        }
                    ),
                )
            )
        return items


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        items = []

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
        items.extend(extension.get_meeting_ext_result_items(argument,
                                                            extension.preferences['open_with_id']))
        return RenderResultListAction(items)


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        data = event.get_data()
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
