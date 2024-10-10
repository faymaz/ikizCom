import { Extension } from 'resource:///org/gnome/shell/extensions/extension.js';
import St from 'gi://St';
import Clutter from 'gi://Clutter';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';

let filePath = GLib.get_home_dir() + '/bg_info.txt';

export default class BGExtension extends Extension {
    enable() {
        this._indicator = new PanelMenu.Button(0.0, this.metadata.name, false);

        // Create St.Label component
        this._label = new St.Label({
            text: 'Loading...',
            y_align: Clutter.ActorAlign.CENTER
        });

        this._indicator.add_child(this._label);
        Main.panel.addToStatusArea(this.metadata.uuid, this._indicator);

        // Update every 1 minute
        this._timeout = GLib.timeout_add_seconds(GLib.PRIORITY_DEFAULT, 60, () => {
            this._updatePanelText();
            return true;
        });

        this._updatePanelText();  // Initial update
    }

    disable() {
        if (this._indicator) {
            this._indicator.destroy();
            this._indicator = null;
        }

        if (this._timeout) {
            GLib.Source.remove(this._timeout);
            this._timeout = null;
        }
    }

    _updatePanelText() {
        try {
            let file = Gio.File.new_for_path(filePath);
            if (!file.query_exists(null)) {
                log("File does not exist: bg_info.txt");
                return;
            }

            let [ok, content] = GLib.file_get_contents(filePath);
            if (!ok) {
                logError(new Error("Failed to read file: bg_info.txt"));
                return;
            }

            let contentStr = content.toString();

            // Remove ANSI color codes and unnecessary parts
            //contentStr = contentStr.replace(/\u001b\[93m|\u001b\[0m/g, '');  // Remove color codes
            contentStr = contentStr.replace(/\u001b\[93m|\u001b\[0m|\u001b\[91m|\u001b\[92m|\033\[91m|\033\[92m/g, '');  // Remove color codes
            contentStr = contentStr.replace(/ at \d{4}-\d{2}-\d{2} (\d{2}:\d{2}):\d{2}/, ' $1');  // Extract only time
            contentStr = contentStr.replace(/(\d+) mg\/dL/, '$1 mg/dL');  // Keep mg/dL part only

            // Log formatted content for debugging
            log(`Formatted content: ${contentStr}`);

            // Update the St.Label widget with cleaned-up text
            if (this._label) {
                this._label.set_text(contentStr);  // Set the cleaned-up text
            } else {
                log("Label not found!");
            }
        } catch (e) {
            logError(e);
        }
    }
}
