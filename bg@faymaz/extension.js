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

        // St.Label bileşeni oluşturuyoruz
        this._label = new St.Label({
            text: 'Loading...',
            y_align: Clutter.ActorAlign.CENTER
        });

        this._indicator.add_child(this._label);
        Main.panel.addToStatusArea(this.metadata.uuid, this._indicator);

        // 1 dakikada bir güncelleme yapılacak
        this._timeout = GLib.timeout_add_seconds(GLib.PRIORITY_DEFAULT, 60, () => {
            this._updatePanelText();
            return true;
        });

        this._updatePanelText();  // Başlangıçta güncelleme yap
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
                log("Dosya mevcut değil: bg_info.txt");
                return;
            }
    
            let [ok, content] = GLib.file_get_contents(filePath);
            if (!ok) {
                logError(new Error("Dosya okunamadı: bg_info.txt"));
                return;
            }
    
            let contentStr = content.toString();
    
            // ANSI renk kodlarını ve gereksiz kısımları temizleyelim
            contentStr = contentStr.replace(/\u001b\[93m|\u001b\[0m/g, '');  // Renk kodlarını kaldır
            contentStr = contentStr.replace(/ at \d{4}-\d{2}-\d{2} (\d{2}:\d{2}):\d{2}/, ' $1');  // Tarihi sadece saat olarak al
            contentStr = contentStr.replace(/(\d+) mg\/dL/, '$1 mg/dL');  // mg/dL kısmını KŞ ile değiştir
            
            // Yalnızca gerekli bilgileri formatlıyoruz
            log(`Düzenlenmiş içerik: ${contentStr}`);
    
            // St.Label bileşenini güncelle
            if (this._label) {
                this._label.set_text(contentStr);  // Düzenlenmiş metni ayarla
            } else {
                log("Label bulunamadı!");
            }
        } catch (e) {
            logError(e);
        }
    }
}