# -*- coding: utf-8 -*-
"""
historico.py
Compatível com telas_e_botoes.py:
- start_session(...)
- set_filters(session_id, areas, dificuldades)
- log_question(session_id, idx, area, difficulty, correct, chosen_option, correct_option,
               response_time_ms, predefined_time_ms, question_id, equipe)
- end_session(session_id, final_scoreboard=None)

Salva 1 sessão por linha em configs/historico_log.jsonl
Inclui HistoricoScreen para visualização + exportação.
"""

import os, sys, json, uuid, time, datetime, csv
from typing import Any, Dict, List, Optional

# ---------------- caminhos ----------------
def _base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.dirname(__file__))

def _ensure_dir():
    os.makedirs(os.path.join(_base_dir(), "configs"), exist_ok=True)

def _hist_path():
    _ensure_dir()
    return os.path.join(_base_dir(), "configs", "historico_log.jsonl")

def _exports_dir():
    path = os.path.join(_base_dir(), "configs", "exports")
    os.makedirs(path, exist_ok=True)
    return path

# ---------------- estado ----------------
_SESS: Dict[str, Dict[str, Any]] = {}

# ---------------- util datas ----------------
_FMT = "%Y-%m-%d %H:%M:%S"

def _now_str() -> str:
    return datetime.datetime.now().strftime(_FMT)

def _from_str(s: str) -> datetime.datetime:
    return datetime.datetime.strptime(s, _FMT)

# ---------------- API -------------------
class HistoryManager:
    @staticmethod
    def start_session(game_mode: str, num_teams: int, time_limit_secs: int,
                      metadata: Optional[Dict[str, Any]] = None) -> str:
        sid = str(uuid.uuid4())
        _SESS[sid] = {
            "session_id": sid,
            "started_at": _now_str(),
            "game_mode": game_mode,
            "num_teams": int(num_teams),
            "time_limit_secs": int(time_limit_secs),
            "areas_selected": [],
            "difficulties_selected": [],
            "rounds": [],
            "final_scoreboard": None,
            "ended_at": None,
            "duration_secs": None,
            "metadata": metadata or {},
        }
        return sid

    @staticmethod
    def set_filters(session_id: str, areas: List[str], dificuldades: List[str]) -> None:
        s = _SESS.get(session_id)
        if not s: return
        s["areas_selected"] = list(areas or [])
        s["difficulties_selected"] = list(dificuldades or [])

    @staticmethod
    def log_question(session_id: str, idx: int, *,
                     area: str, difficulty: str, correct: bool,
                     chosen_option: Optional[Any], correct_option: Optional[Any],
                     response_time_ms: Optional[int],
                     predefined_time_ms: Optional[int],
                     question_id: str,
                     equipe: Optional[int] = None) -> None:
        s = _SESS.get(session_id)
        if not s: return
        q = {
            "index": idx,
            "question_id": question_id,
            "area": area,
            "difficulty": difficulty,
            "answer_marked": chosen_option,
            "correct_answer": correct_option,
            "is_correct": bool(correct),
            "answer_time_secs": None if response_time_ms is None else round(response_time_ms / 1000.0, 2),
            "predefined_time_secs": None if predefined_time_ms is None else int(predefined_time_ms / 1000),
            "equipe": equipe,
            "answered_at": _now_str(),
        }
        s["rounds"].append(q)   # REGISTRA A PERGUNTA

    @staticmethod
    def end_session(session_id: str, final_scoreboard: Any = None) -> None:
        s = _SESS.get(session_id)
        if not s: return
        s["final_scoreboard"] = final_scoreboard
        s["ended_at"] = _now_str()
        try:
            t0 = _from_str(s["started_at"])
            t1 = _from_str(s["ended_at"])
            s["duration_secs"] = int((t1 - t0).total_seconds())
        except Exception:
            s["duration_secs"] = None
        with open(_hist_path(), "a", encoding="utf-8") as f:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    @staticmethod
    def load_all_sessions() -> List[Dict[str, Any]]:
        p = _hist_path()
        if not os.path.exists(p): return []
        out = []
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try: out.append(json.loads(line))
                    except: pass
        return out

# -------- Tela de Histórico --------
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.metrics import dp

class HistoricoScreen(Screen):
    name = "historico_screen"

    def on_pre_enter(self, *args):
        self._build()

    def _build(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        # Barra superior com Voltar
        topbar = BoxLayout(size_hint=(1, None), height=dp(48), spacing=dp(8))
        btn_back = Button(text="Voltar", size_hint=(None, 1), width=dp(120), font_size=dp(16))
        btn_back.bind(on_release=lambda *_: setattr(self.manager, "current", "tela_inicial"))
        topbar.add_widget(btn_back)
        root.add_widget(topbar)

        sc = ScrollView(size_hint=(1, 1))
        col = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8), padding=[0, 0, 0, dp(6)])
        col.bind(minimum_height=col.setter("height"))

        sessions = list(reversed(HistoryManager.load_all_sessions()))
        if not sessions:
            col.add_widget(Label(text="Nenhuma sessão registrada ainda.", font_size=dp(18)))
        else:
            for ses in sessions:
                btn = Button(
                    text=self._header(ses),
                    size_hint_y=None, height=dp(56),
                    font_size=dp(16),
                    halign="left", valign="middle",
                    padding=(dp(12), dp(12))
                )
                def _resize_text(instance, size):
                    instance.text_size = (size[0] - dp(24), None)
                btn.bind(size=_resize_text)
                _resize_text(btn, (btn.width, btn.height))
                btn.bind(on_release=lambda b, s=ses: self._open(s))
                col.add_widget(btn)

        sc.add_widget(col)
        root.add_widget(sc)
        self.add_widget(root)

    def _header(self, s: Dict[str, Any]) -> str:
        started = s.get("started_at", "")
        gm = s.get("game_mode", "?")
        teams = s.get("num_teams", "?")
        tl = s.get("time_limit_secs", "?")
        dur = s.get("duration_secs")
        return f" {started} | Modo: {gm} | Equipes: {teams} | Tempo/questão: {tl}s | Duração: {dur or '—'}s"

    def _open(self, s: Dict[str, Any]):
        sep = "-" * 80
        areas_str = ", ".join(s.get("areas_selected") or [])
        dific_str = ", ".join(s.get("difficulties_selected") or [])

        lines = []
        lines.append(self._header(s))
        lines.append(sep)
        lines.append(f"[b]Áreas:[/b] {areas_str if areas_str else '—'}")
        lines.append(f"[b]Dificuldades:[/b] {dific_str if dific_str else '—'}")
        lines.append("")

        for i, r in enumerate(s.get("rounds", []), 1):
            equipe_txt = f" | Equipe {r.get('equipe')}" if r.get('equipe') is not None else ""
            lines.append(f"{i:02d}. [{r.get('area','')} | {r.get('difficulty','')}{equipe_txt}]")
            q_show = r.get("question") or r.get("question_id", "")
            lines.append(f"    Pergunta: {q_show}")
            lines.append(
                f"    Resposta: {r.get('answer_marked')!r} | Correta: {r.get('correct_answer')!r} "
                f"| Resultado: {'Certo' if r.get('is_correct') else 'Errado'}"
            )
            lines.append(f"    Tempo gasto: {r.get('answer_time_secs','—')} s")
            lines.append("")

        fs = s.get("final_scoreboard")
        if fs is not None:
            lines.append("Placar final:")
            if isinstance(fs, dict):
                for k, v in fs.items():
                    lines.append(f"    {k}: {v}")
            else:
                lines.append(f"    {fs}")

        padding = dp(12)
        inner = BoxLayout(orientation="vertical",
                          size_hint_y=None,
                          padding=(dp(10), dp(8), dp(10), dp(8)),
                          spacing=dp(6))
        inner.bind(minimum_height=inner.setter("height"))

        lbl = Label(
            text="\n".join(lines),
            halign="left", valign="top",
            size_hint=(1, None),
            markup=True
        )
        lbl.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))
        lbl.bind(width=lambda inst, w: setattr(inst, "text_size", (w, None)))
        inner.add_widget(lbl)

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(inner)

        btn_row = BoxLayout(size_hint=(1, None), height=dp(52), spacing=dp(10), padding=[dp(10), 0, dp(10), 0])
        btn_export = Button(text="EXPORTAR", size_hint=(None, 1), width=dp(140), font_size=dp(16))
        btn_close = Button(text="Fechar", size_hint=(None, 1), width=dp(120), font_size=dp(16))
        btn_row.add_widget(btn_export)
        btn_row.add_widget(btn_close)

        box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        box.add_widget(scroll)
        box.add_widget(btn_row)

        popup = Popup(
            title="Detalhes da Sessão",
            content=box,
            size_hint=(None, None), size=(dp(900), dp(600))
        )

        def _do_export(*_):
            txt_path, csv_path = self._export_session(s)
            info = f"Exportado com sucesso:\n\nTXT: {txt_path}\nCSV: {csv_path}"
            Popup(
                title="Exportação concluída",
                content=Label(
                    text=info,
                    halign="left",
                    valign="top",
                    markup=True,
                    text_size=(dp(580), None)
                ),
                size_hint=(None, None),
                size=(dp(600), dp(300))
            ).open()

        btn_export.bind(on_release=_do_export)
        btn_close.bind(on_release=lambda *_: popup.dismiss())
        popup.open()

    # ---------- Exportação ----------
    def _export_session(self, ses: Dict[str, Any]):
        export_dir = _exports_dir()
        started = ses.get("started_at", "").replace(":", "-")
        sid = ses.get("session_id", "sessao")
        base = f"{started}_{sid[:8]}"
        txt_path = os.path.join(export_dir, f"{base}.txt")
        csv_path = os.path.join(export_dir, f"{base}.csv")

        sep = "-" * 80
        areas_str = ", ".join(ses.get("areas_selected") or [])
        diffs_str = ", ".join(ses.get("difficulties_selected") or [])
        lines = []
        lines.append(f"{ses.get('started_at','')} | Modo: {ses.get('game_mode','')} | "
                     f"Equipes: {ses.get('num_teams','')} | Tempo/questão: {ses.get('time_limit_secs','')}s | "
                     f"Duração: {ses.get('duration_secs','—')}s")
        lines.append(sep)
        lines.append(f"Áreas: {areas_str if areas_str else '—'}")
        lines.append(f"Dificuldades: {diffs_str if diffs_str else '—'}")
        lines.append("")
        for i, r in enumerate(ses.get("rounds", []), 1):
            equipe_txt = f" | Equipe {r.get('equipe')}" if r.get('equipe') is not None else ""
            lines.append(f"{i:02d}. [{r.get('area','')} | {r.get('difficulty','')}{equipe_txt}]")
            q_show = r.get("question") or r.get("question_id", "")
            lines.append(f"    Pergunta: {q_show}")
            lines.append(f"    Resposta: {r.get('answer_marked')!r} | Correta: {r.get('correct_answer')!r} "
                         f"| Resultado: {'CORRETA' if r.get('is_correct') else 'ERRADA'}")
            lines.append(f"    Tempo gasto: {r.get('answer_time_secs','—')} s")
            lines.append("")
        fs = ses.get("final_scoreboard")
        if fs is not None:
            lines.append("Placar final:")
            if isinstance(fs, dict):
                for k, v in fs.items():
                    lines.append(f"    {k}: {v}")
            else:
                lines.append(f"    {fs}")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        headers = [
            "session_id", "started_at", "ended_at", "duration_secs",
            "game_mode", "num_teams", "time_limit_secs",
            "areas_selected", "difficulties_selected",
            "index", "area", "difficulty", "equipe",
            "question", "answer_marked", "correct_answer",
            "is_correct", "answer_time_secs", "predefined_time_secs", "answered_at"
        ]
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers, delimiter=";")
            writer.writeheader()
            areas_join = ", ".join(ses.get("areas_selected") or [])
            diffs_join = ", ".join(ses.get("difficulties_selected") or [])
            for r in ses.get("rounds", []):
                row = {
                    "session_id": ses.get("session_id"),
                    "started_at": ses.get("started_at"),
                    "ended_at": ses.get("ended_at"),
                    "duration_secs": ses.get("duration_secs"),
                    "game_mode": ses.get("game_mode"),
                    "num_teams": ses.get("num_teams"),
                    "time_limit_secs": ses.get("time_limit_secs"),
                    "areas_selected": areas_join,
                    "difficulties_selected": diffs_join,
                    "index": r.get("index"),
                    "area": r.get("area"),
                    "difficulty": r.get("difficulty"),
                    "equipe": r.get("equipe"),
                    "question": r.get("question") or r.get("question_id"),
                    "answer_marked": r.get("answer_marked"),
                    "correct_answer": r.get("correct_answer"),
                    "is_correct": r.get("is_correct"),
                    "answer_time_secs": r.get("answer_time_secs"),
                    "predefined_time_secs": r.get("predefined_time_secs"),
                    "answered_at": r.get("answered_at"),
                }
                writer.writerow(row)

        return txt_path, csv_path
