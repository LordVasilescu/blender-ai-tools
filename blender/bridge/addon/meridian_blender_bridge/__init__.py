# © 2026 Mathew. All rights reserved.
bl_info = {
    "name": "Meridian Bridge (Grok live)",
    "author": "Mathew Vasilescu",
    "version": (1, 3, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Meridian",
    "description": "Stable inbox/outbox bridge for Grok. Leave Blender open; never launch Blender under the agent Job Object.",
    "category": "Development",
}

import bpy
import json
import os
import traceback
from pathlib import Path
from datetime import datetime

BRIDGE_ROOT = Path(os.environ.get("MERIDIAN_BL_BRIDGE", r"C:\Users\Mathe\Meridian\tools\blender_bridge"))
INBOX = BRIDGE_ROOT / "inbox"
OUTBOX = BRIDGE_ROOT / "outbox"
STATUS = BRIDGE_ROOT / "status.json"

_timer_running = False
POLL_SEC = 0.4
HEARTBEAT_EVERY = 2.0  # seconds
_last_heartbeat = 0.0


def _ensure_dirs():
    try:
        INBOX.mkdir(parents=True, exist_ok=True)
        OUTBOX.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass


def _write_status(state: str, detail: str = "", last_job: str = ""):
    """Always write fresh status so bctl can see the bridge is alive."""
    global _last_heartbeat
    _ensure_dirs()
    blend = "(unknown)"
    objects = -1
    try:
        blend = bpy.data.filepath or "(unsaved)"
        objects = len(bpy.data.objects)
    except Exception:
        pass
    data = {
        "state": state,
        "detail": detail,
        "time": datetime.now().isoformat(timespec="seconds"),
        "blend": blend,
        "objects": objects,
        "bridge": "meridian_blender_bridge",
        "version": "1.3-visible-grok",
        "running": bool(_timer_running),
        "last_job": last_job or "",
        "inbox": str(INBOX),
        "pid": os.getpid(),
    }
    try:
        STATUS.write_text(json.dumps(data, indent=2), encoding="utf-8")
        _last_heartbeat = datetime.now().timestamp()
    except Exception:
        pass


def _view3d_override():
    """Safe context for operators — missing this can CRASH Blender from a timer."""
    try:
        wm = bpy.context.window_manager
        for window in wm.windows:
            screen = window.screen
            if screen is None:
                continue
            for area in screen.areas:
                if area.type != "VIEW_3D":
                    continue
                region = None
                for r in area.regions:
                    if r.type == "WINDOW":
                        region = r
                        break
                if region is None and area.regions:
                    region = area.regions[-1]
                return {
                    "window": window,
                    "screen": screen,
                    "area": area,
                    "region": region,
                }
    except Exception:
        pass
    return None


def _run_command_file(path: Path) -> dict:
    result = {"ok": False, "file": path.name, "output": "", "error": "", "id": path.stem}
    try:
        raw = path.read_text(encoding="utf-8-sig")
        if path.suffix.lower() == ".py":
            code = raw
            cmd_id = path.stem
            if cmd_id.startswith("_running_"):
                cmd_id = cmd_id[len("_running_") :]
        else:
            payload = json.loads(raw)
            code = payload.get("code", "")
            cmd_id = payload.get("id", path.stem)

        import io
        import sys

        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            ns = {"bpy": bpy, "__name__": "__main__"}
            compiled = compile(code, str(path), "exec")
            ov = _view3d_override()
            if ov is not None:
                with bpy.context.temp_override(**ov):
                    exec(compiled, ns, ns)
            else:
                exec(compiled, ns, ns)
        finally:
            sys.stdout = old

        result["ok"] = True
        result["id"] = cmd_id
        result["output"] = buf.getvalue()
        _write_status("listening", f"last_ok={path.name}", last_job=cmd_id)
    except Exception:
        result["error"] = traceback.format_exc()
        _write_status("error", path.name, last_job=path.stem)
    return result


def _poll():
    """Timer callback — MUST never raise or Blender can die."""
    global _timer_running, _last_heartbeat
    try:
        if not _timer_running:
            return None

        _ensure_dirs()
        now = datetime.now().timestamp()
        if now - _last_heartbeat >= HEARTBEAT_EVERY:
            _write_status("listening", "heartbeat")

        files = sorted(
            list(INBOX.glob("*.py")) + list(INBOX.glob("*.json")),
            key=lambda p: p.stat().st_mtime,
        )
        files = [f for f in files if not f.name.startswith("_") and f.name != "_README.txt"]

        if files:
            path = files[0]
            # Use clean job id for result matching (like uectl)
            job_stem = path.stem
            running = INBOX / f"_running_{path.name}"
            try:
                if running.exists():
                    running.unlink()
                path.replace(running)
            except Exception:
                running = path

            _write_status("busy", f"running {running.name}", last_job=job_stem)
            res = _run_command_file(running)
            # result_*JOBNAME*.json for bctl matching
            stamp = datetime.now().strftime("%H%M%S")
            out_name = f"result_{stamp}_{job_stem}.json"
            try:
                (OUTBOX / out_name).write_text(json.dumps(res, indent=2), encoding="utf-8")
            except Exception:
                pass
            try:
                running.unlink(missing_ok=True)
            except Exception:
                pass
            try:
                if bpy.context.screen:
                    for area in bpy.context.screen.areas:
                        if area.type == "VIEW_3D":
                            area.tag_redraw()
            except Exception:
                pass
            print(f"[Meridian Bridge] ok={res.get('ok')} job={job_stem}")

        return POLL_SEC
    except Exception:
        print("[Meridian Bridge] poll error:\n", traceback.format_exc())
        try:
            _write_status("error", "poll exception")
        except Exception:
            pass
        return POLL_SEC


def _start_timer():
    global _timer_running
    _ensure_dirs()
    _timer_running = True
    # File load wipes timers. Always re-register if the poller is gone.
    if not bpy.app.timers.is_registered(_poll):
        bpy.app.timers.register(_poll, first_interval=0.4)
        print(f"[Meridian Bridge] listening on {INBOX}")
    _write_status("listening", str(INBOX))


def _stop_timer():
    global _timer_running
    _timer_running = False
    try:
        if bpy.app.timers.is_registered(_poll):
            bpy.app.timers.unregister(_poll)
    except Exception:
        pass
    _write_status("stopped", "")
    print("[Meridian Bridge] stopped")


class MERIDIAN_OT_bridge_start(bpy.types.Operator):
    bl_idname = "meridian.bridge_start"
    bl_label = "Start Bridge"

    def execute(self, context):
        _start_timer()
        self.report({"INFO"}, "Meridian Bridge listening")
        return {"FINISHED"}


class MERIDIAN_OT_bridge_stop(bpy.types.Operator):
    bl_idname = "meridian.bridge_stop"
    bl_label = "Stop Bridge"

    def execute(self, context):
        _stop_timer()
        self.report({"INFO"}, "Meridian Bridge stopped")
        return {"FINISHED"}


class MERIDIAN_PT_bridge_panel(bpy.types.Panel):
    bl_label = "Meridian Bridge"
    bl_idname = "MERIDIAN_PT_bridge"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Meridian"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Grok live (stable)")
        layout.operator("meridian.bridge_start", icon="PLAY")
        layout.operator("meridian.bridge_stop", icon="PAUSE")
        layout.separator()
        layout.label(text="Leave Blender open")
        if STATUS.exists():
            try:
                st = json.loads(STATUS.read_text(encoding="utf-8"))
                layout.label(text=f"State: {st.get('state', '?')}")
                layout.label(text=f"v{st.get('version', '?')}")
            except Exception:
                pass


classes = (
    MERIDIAN_OT_bridge_start,
    MERIDIAN_OT_bridge_stop,
    MERIDIAN_PT_bridge_panel,
)


@bpy.app.handlers.persistent
def _on_load_post(_dummy):
    try:
        _start_timer()
        print("[Meridian Bridge] restarted after file load")
    except Exception as e:
        print("[Meridian Bridge] load_post restart failed:", e)


def register():
    for c in classes:
        bpy.utils.register_class(c)

    if _on_load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_on_load_post)

    def _deferred_start():
        try:
            _start_timer()
            print("[Meridian Bridge] LISTENING — leave Blender open")
        except Exception as e:
            print("[Meridian Bridge] start failed:", e)
        return None

    try:
        bpy.app.timers.register(_deferred_start, first_interval=1.5)
    except Exception as e:
        print("[Meridian Bridge] timer failed:", e)


def unregister():
    try:
        if _on_load_post in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.remove(_on_load_post)
    except Exception:
        pass
    _stop_timer()
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
