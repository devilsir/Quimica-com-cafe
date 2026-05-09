import sys
import os
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.behaviors import DragBehavior, ButtonBehavior
from kivy.properties import BooleanProperty, StringProperty


def resource_path_full(relative_path: str, subfolder: str = "") -> str:
    """
    Resolve caminho de arquivo tanto em modo script quanto em executável (PyInstaller).
    """
    if getattr(sys, "frozen", False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, subfolder, relative_path) if subfolder else os.path.join(base_path, relative_path)


# ---- Dados dos popups (1 por pessoa) ----
# Só 3 infos: nome, função e descrição.
# "imagem_popup" é a imagem que aparece dentro do popup (ex.: versão com borda/glow).
CREDITOS_DADOS = [
    {
        "nome": "Lucas Xavier Nardelli",
        "funcao": "Desenvolvedor",
        "descricao": "Responsável pelo desenvolvimento do aplicativo, implementação das funcionalidades e artes. Professor da educação básica. Projeto desenvolvido na graduação como parte da monografia aprsentada para conclusão do curso.",
        "imagem_popup": "LucasB.png",
        "popup_bg": "PopupC.png",
    },
    {
        "nome": "Angel Amado Recio Despaigne",
        "funcao": "Orientador / Revisor",
        "descricao": "Apoio técnico, revisão e contribuições para o refinamento do conteúdo. Doutor em Química pela Universidade Federal de Minas Gerais (2012), e Bacharel em Química pela Universidad de Oriente, (1995). Atualmente é Professor Adjunto IV no Departamento de Química da Universidade Federal de Viçosa . Anteriormente, atuou como Professor Adjunto no Departamento de Química da Universidad de Oriente. Exerce a coordenação do Programa de Mestrado Profissional em Química em Rede Nacional (PROFQUI). Possui experiência e atuação na área de Química, com ênfase em Química Medicinal Inorgânica, dedicando-se principalmente à síntese e caracterização de compostos metálicos com propriedades biológicas.",
        "imagem_popup": "AngelB.png",
        "popup_bg": "PopupC.png",
    },
    {
        "nome": "Fábio Junior Moreira Novaes",
        "funcao": "Coorientador / Revisor",
        "descricao": "Apoio técnico, revisão e contribuições para o refinamento do conteúdo. Professor de Química Geral e Analítica do Departamento de Química da Universidade Federal do Viçosa, atuando nos Programas de Pós-Graduação em Agroquímica e no Mestrado Profissional em Química em Rede Nacional. É colíder do grupo de pesquisa LaQuA - Química Analítica Aplicada, onde realiza pesquisas em Química e Análise de Alimentos . Outros estudos na área de jogos e metodologias ativas para o Ensino de Química também compõem as áreas de atuação.",
        "imagem_popup": "FabioB.png",
        "popup_bg": "PopupC.png",
    },
    {
        "nome": "Viviane",
        "funcao": "Coorientadora / Revisora",
        "descricao": "Apoio, revisão e direcionamentos para melhorar clareza e didática do material. Professora de Educação Básica, atuando como Diretora de escola da Rede Estadual de Ensino - SEEMG. Graduada em QUÍMICA pela UNIVERSIDADE DE ITAÚNA. Pós-graduada em Ensino de Química pela Faculdade Facuminas. Mestranda pela UFV, no programa PROFQUI - Mestrado Profissional em Química em Rede Nacional.",
        "imagem_popup": "VivianeB.png",
        "popup_bg": "PopupC.png",
    },
]


class TelaCreditos(Screen):
    """
    Tela de créditos com 4 botões (fotos) e popup individual pra cada pessoa.
    """

    def abrir_credito(self, idx: int):
        """
        Abre um popup de crédito de acordo com o índice do botão clicado.
        Layout estilo "Ficha", com imagem à esquerda e infos à direita.
        """
        try:
            idx_int = int(idx)
        except Exception:
            return

        if idx_int < 0 or idx_int >= len(CREDITOS_DADOS):
            return

        item = CREDITOS_DADOS[idx_int]

        # --- Conteúdo do popup ---
        root = BoxLayout(orientation="vertical", padding=[dp(26), dp(24), dp(26), dp(18)], spacing=dp(16))

        # Cabeçalho (estilo ficha)
        header = Label(
            text="[color=8F6FA0][b]FICHA DE PERSONAGEM[/b][/color]",
            markup=True,
            font_size="40sp",
            size_hint=(1, None),
            height=dp(56),
            halign="center",
            valign="middle",
        )
        header.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))

        # Linha separadora (simples)
        line = Label(
            text="[color=8F6FA0]______________________________________________[/color]",
            markup=True,
            font_size="22sp",
            size_hint=(1, None),
            height=dp(20),
            halign="center",
            valign="middle",
        )
        line.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))

        root.add_widget(header)
        root.add_widget(line)

        # Miolo: imagem à esquerda + infos à direita
        body = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint=(1, 1))

        img_src = item.get("imagem_popup") or ""
        img_src = item.get("imagem_popup") or ""

        # Wrapper pra alinhar topo (imagem e texto)
        left_wrap = AnchorLayout(size_hint=(0.32, 1), anchor_x="right", anchor_y="top", padding=(0, dp(18), dp(8), 0))
        img = Image(
            source=resource_path_full(img_src, "assets") if img_src else "",
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(None, None),
        )
        left_wrap.add_widget(img)

        info_wrap = AnchorLayout(size_hint=(0.68, 1), anchor_x="left", anchor_y="top", padding=(dp(8), dp(18), 0, 0))
        info = BoxLayout(orientation="vertical", spacing=dp(12), size_hint=(1, None))
        info.bind(minimum_height=info.setter("height"))
        info_wrap.add_widget(info)

        def _fit_img(*_args):
            if not img.texture:
                return
            tw, th = img.texture.size
            max_w = left_wrap.width
            max_h = body.height
            if max_w <= 1 or max_h <= 1 or tw <= 1 or th <= 1:
                return
            scale = min(max_w / tw, max_h / th)
            img.size = (tw * scale, th * scale)

        img.bind(texture=_fit_img)
        left_wrap.bind(size=_fit_img)
        body.bind(size=_fit_img)

        def mk_row(titulo: str, valor: str) -> Label:
            lbl = Label(
                text=f"[color=8F6FA0][b]{titulo}:[/b][/color] {valor}",
                markup=True,
                font_size="22sp",
                halign="justify",
                valign="top",
                color=(1, 1, 1, 1),
                size_hint=(1, None),
            )
            # altura "auto" baseada no texto (via texture)
            lbl.bind(texture_size=lambda inst, *_: setattr(inst, "height", inst.texture_size[1] + dp(6)))
            lbl.bind(size=lambda inst, *_: setattr(inst, "text_size", (inst.width, None)))
            return lbl

        nome_lbl = mk_row("Nome", item.get("nome", ""))
        func_lbl = mk_row("Função", item.get("funcao", ""))
        desc_lbl = mk_row("Descrição", item.get("descricao", ""))

        info.add_widget(nome_lbl)
        info.add_widget(func_lbl)
        info.add_widget(desc_lbl)

        body.add_widget(left_wrap)
        body.add_widget(info_wrap)

        root.add_widget(body)

        # Botão fechar
        btn_row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(52))
        btn_row.add_widget(Label(size_hint=(1, 1)))  # espaçador
        btn_fechar = Button(
    text="Fechar",
    size_hint=(None, 1),
    width=dp(160),
    background_normal="",   # remove a textura padrão (senão a cor não pega direito)
    background_down="",     # remove a textura do clique
    background_color=(0.55, 0.35, 0.75, 1),  # roxo
    color=(1, 1, 1, 1)      # texto branco
)
        btn_row.add_widget(btn_fechar)
        root.add_widget(btn_row)

        # Background do popup (usa Popuplucas.png por padrão)
        bg = item.get("popup_bg")
        bg_path = resource_path_full(bg, "assets")

        popup = Popup(
            title="",
            separator_height=0,
            content=root,
            size_hint=(0.86, 0.88),
            background=bg_path,
            overlay_color=(0, 0, 0, 0.92),
            background_color=(1, 1, 1, 1),
            auto_dismiss=False,
        )

        btn_fechar.bind(on_release=lambda *_: popup.dismiss())
        popup.open()

    def voltar(self):
        if self.manager:
            self.manager.current = "tela_inicial"


class HoverDraggableImageButton(DragBehavior, ButtonBehavior, Image):
    """
    ImageButton com hover/down (troca o source) e drag.
    """
    source_normal = StringProperty("")
    source_hover = StringProperty("")
    source_down = StringProperty("")
    _hovered = BooleanProperty(False)
    _pressed = BooleanProperty(False)

    def on_kv_post(self, base_widget):
        if not self.source_normal:
            self.source_normal = self.source

        if not self.source_hover and self.source_normal:
            self.source_hover = self._add_suffix(self.source_normal, "_hover")
        if not self.source_down and self.source_normal:
            self.source_down = self._add_suffix(self.source_normal, "_down")

        self.source = self.source_normal
        Window.bind(mouse_pos=self.on_mouse_pos)

    def _add_suffix(self, filename, suffix):
        name, ext = os.path.splitext(filename)
        return f"{name}{suffix}{ext}" if ext else filename

    def on_mouse_pos(self, window, pos):
        if not self.get_root_window():
            return

        inside = self.collide_point(*self.to_widget(*pos))
        if inside != self._hovered:
            self._hovered = inside
            if not self._pressed:
                self._apply_visual_state()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._pressed = True
            self._apply_visual_state(down=True)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        was_pressed = self._pressed
        self._pressed = False
        if was_pressed:
            self._apply_visual_state()
        return super().on_touch_up(touch)

    def _apply_visual_state(self, down=False):
        if down:
            self.source = self.source_down or self.source_normal
            return

        if self._hovered and self.source_hover:
            self.source = self.source_hover
        else:
            self.source = self.source_normal


_KV = r"""
#:import resource_path_full creditos.resource_path_full
#:import dp kivy.metrics.dp

<TelaCreditos>:
    name: 'tela_creditos'

    FloatLayout:
        Image:
            source: resource_path_full('fundo_creditos.png', 'assets')
            allow_stretch: True
            keep_ratio: False
            size_hint: 1, 1
            pos_hint: {'x': 0, 'y': 0}

        Label:
            text: 'Créditos'
            font_size: dp(40)
            color: 1, 1, 1, 1
            bold: True
            size_hint: None, None
            size: dp(400), dp(60)
            pos_hint: {'center_x': 0.5, 'top': 0.98}

        BoxLayout:
            size_hint: None, None
            size: dp(850), dp(400)
            pos_hint: {'center_x': 0.5, 'center_y': 0.4}
            spacing: dp(20)
            orientation: 'horizontal'

            HoverDraggableImageButton:
                source: resource_path_full('Lucas.png', 'assets')
                source_normal: resource_path_full('Lucas.png', 'assets')
                source_hover: resource_path_full('LucasB.png', 'assets')
                source_down: resource_path_full('LucasB.png', 'assets')
                size_hint: 0.25, 1
                on_release: root.abrir_credito(0)

            HoverDraggableImageButton:
                source: resource_path_full('Angel.png', 'assets')
                source_normal: resource_path_full('Angel.png', 'assets')
                source_hover: resource_path_full('AngelB.png', 'assets')
                source_down: resource_path_full('AngelB.png', 'assets')
                size_hint: 0.25, 1
                on_release: root.abrir_credito(1)

            HoverDraggableImageButton:
                source: resource_path_full('Fabio.png', 'assets')
                source_normal: resource_path_full('Fabio.png', 'assets')
                source_hover: resource_path_full('FabioB.png', 'assets')
                source_down: resource_path_full('FabioB.png', 'assets')
                size_hint: 0.25, 1
                on_release: root.abrir_credito(2)

            HoverDraggableImageButton:
                source: resource_path_full('Viviane.png', 'assets')
                source_normal: resource_path_full('Viviane.png', 'assets')
                source_hover: resource_path_full('VivianeB.png', 'assets')
                source_down: resource_path_full('VivianeB.png', 'assets')
                size_hint: 0.25, 1
                on_release: root.abrir_credito(3)

        HoverDraggableImageButton:
            source: resource_path_full('setavoltar.png', 'assets')
            source_normal: resource_path_full('setavoltar.png', 'assets')
            source_hover: resource_path_full('setavoltar_hover.png', 'assets')
            source_down: resource_path_full('setavoltar_hover.png', 'assets')
            border: 0, 0, 0, 0
            size_hint: None, None
            size: dp(60), dp(60)
            pos_hint: {'x': 0.02, 'top': 0.95}
            on_release: root.manager.current = 'intro_screen'
"""

if not globals().get("_CREDITOS_KV_LOADED", False):
    Builder.load_string(_KV)
    globals()["_CREDITOS_KV_LOADED"] = True
