import os
import subprocess

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.ExtensionCustomAction import \
    ExtensionCustomAction
from ulauncher.api.shared.action.RenderResultListAction import \
    RenderResultListAction
from ulauncher.api.shared.event import ItemEnterEvent, KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem


def scan_workspaces(workspaces_root):
    workspaces = [
        ws for ws in os.listdir(workspaces_root) if os.path.isdir(os.path.join(workspaces_root, ws))
    ]

    return workspaces


class DemoExtension(Extension):
    def __init__(self):
        super(DemoExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        workspaces_root = os.path.expanduser(extension.preferences['workspaces_root'])
        workspaces = scan_workspaces(workspaces_root)

        # Filter by query if inserted
        query = event.get_argument()
        if query:
            query = query.strip().lower()
            for ws in workspaces:
                name = ws.lower()
                if query not in name:
                    workspaces.pop(ws)

        # Create launcher entries
        entries = []
        for ws in workspaces:
            entries.append(ExtensionResultItem(
                icon='images/icon.png',
                name=ws,
                description=ws,
                on_enter=ExtensionCustomAction({
                    'open_cmd': extension.preferences['open_cmd'],
                    'opt': [os.path.join(workspaces_root, ws)]
                }, keep_app_open=True)
            ))
        return RenderResultListAction(entries)


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        # Open Chrome when user selects an entry
        data = event.get_data()
        cmd_path = data['open_cmd']
        opt = data['opt']
        subprocess.Popen([cmd_path] + opt)


if __name__ == '__main__':
    DemoExtension().run()
