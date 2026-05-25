from .config import load_config
from .alarms import alarm_rules
from .app import Print2PanelApp


def main():
    cfg = load_config()
    alarm_rules.update(cfg.get("alarms", {}))
    mode = cfg.get("mode", "SIMULATION").upper()

    app = Print2PanelApp(mode=mode, config=cfg)
    app.mainloop()


if __name__ == "__main__":
    main()
