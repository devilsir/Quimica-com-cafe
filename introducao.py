import sys
import os
import json
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.video import Video
from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior, DragBehavior
from kivy.uix.image import Image
from kivy.app import App
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import BooleanProperty, StringProperty
try:
    from kivy.core.video import Video as CoreVideoProvider
except Exception:
    CoreVideoProvider = None


def resource_path_full(relative_path, subfolder=""):
    """Monta caminho correto para assets no modo pasta normal (sem MEI)"""
    if getattr(sys, 'frozen', False):
        # Se for executável PyInstaller
        base_path = os.path.dirname(sys.executable)
    else:
        # Se for rodando em Python normal
        base_path = os.path.abspath(".")
    
    if subfolder:
        return os.path.join(base_path, subfolder, relative_path)
    return os.path.join(base_path, relative_path)
# Definir base_path correto (se .exe, usa pasta do exe)
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.abspath(os.path.dirname(__file__))

LARGURA_ORIGINAL = 1366
ALTURA_ORIGINAL = 705

def calcular_viewport():
    largura = Window.width or LARGURA_ORIGINAL
    altura = Window.height or ALTURA_ORIGINAL
    if largura < 200 or altura < 200:
        largura, altura = LARGURA_ORIGINAL, ALTURA_ORIGINAL

    aspect_original = LARGURA_ORIGINAL / ALTURA_ORIGINAL
    aspect_tela = largura / altura
    if aspect_tela > aspect_original:
        altura_viewport = altura
        largura_viewport = altura * aspect_original
    else:
        largura_viewport = largura
        altura_viewport = largura / aspect_original
    offset_x = (largura - largura_viewport) / 2
    offset_y = (altura - altura_viewport) / 2
    return largura_viewport, altura_viewport, offset_x, offset_y

def ajustar_posicao_letterbox(posicao_salva):
    largura_viewport, altura_viewport, offset_x, offset_y = calcular_viewport()
    return [
        posicao_salva[0] * (largura_viewport / LARGURA_ORIGINAL) + offset_x,
        posicao_salva[1] * (altura_viewport / ALTURA_ORIGINAL) + offset_y,
    ]

def normalizar_posicao(pos):
    largura_viewport, altura_viewport, offset_x, offset_y = calcular_viewport()
    return [
        (pos[0] - offset_x) * (LARGURA_ORIGINAL / largura_viewport),
        (pos[1] - offset_y) * (ALTURA_ORIGINAL / altura_viewport),
    ]

class DraggableSpinner(DragBehavior, Spinner):
    pass
class HoverDraggableImageButton(DragBehavior, ButtonBehavior, Image):
    source_normal = StringProperty('')
    source_hover = StringProperty('')
    source_down = StringProperty('')
    arrastavel = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source_normal = kwargs.get('source', '')
        self.source_hover = self._add_suffix(self.source_normal, '_hover')
        self.source_down = self._add_suffix(self.source_normal, '_hover')
        self.source = self.source_normal
        Window.bind(mouse_pos=self.on_mouse_pos)

    def _add_suffix(self, filename, suffix):
        name, ext = os.path.splitext(filename)
        return f"{name}{suffix}{ext}" if ext.lower() in ['.png', '.jpg', '.jpeg', '.webp'] else filename

    def on_mouse_pos(self, window, pos):
        if not self.get_root_window():
            return
        if self.collide_point(*self.to_widget(*pos)) and os.path.exists(self.source_hover):
            self.source = self.source_hover
        else:
            self.source = self.source_normal

    def on_press(self):
        if os.path.exists(self.source_down):
            self.source = self.source_down

    def on_release(self):
        pos = Window.mouse_pos
        if self.get_root_window() and self.collide_point(*self.to_widget(*pos)) and os.path.exists(self.source_hover):
            self.source = self.source_hover
        else:
            self.source = self.source_normal

# Função auxiliar para criar popups simples com botão Ok
def show_message_popup(title, message):
    content = BoxLayout(
        orientation='vertical',
        spacing=dp(15),
        padding=dp(20)
    )

    # Texto da mensagem
    label = Label(
        text=message,
        font_size=dp(18),
        color=(1, 1, 1, 1)
    )

    # Botão OK com imagem de fundo
    ok_button = Button(
        text="OK",
        size_hint_y=None,
        height=dp(48),
        font_size=dp(20),
        color=(1, 1, 1, 1),
        background_normal=resource_path_full('botao generico popup generico.png', 'assets'),
        background_down=resource_path_full('botao generico popup generico.png', 'assets')
    )

    content.add_widget(label)
    content.add_widget(ok_button)

    # Popup com imagem personalizada de fundo
    popup = Popup(
        title='',
        separator_height=0,
        background=resource_path_full('popup genérico HD.png', 'assets'),
        background_color=(1, 1, 1, 1),
        content=content,
        size_hint=(0.6, 0.4)
    )

    ok_button.bind(on_press=lambda *args: popup.dismiss())
    popup.open()
    return popup

class ConfigMenu(BoxLayout):
    popup_ref = None  # será preenchido no open_mode_popup

    def confirmar(self):
        if self.ids.spinner_mode.text == 'Clique para escolher':
            show_message_popup("Erro", "Por favor, escolha um modo de jogo!")
            return
        tela = App.get_running_app().root.get_screen('tela_inicial')
        tela.ids.spinner_game_mode.text = self.ids.spinner_mode.text
        tela.ids.spinner_equipes.text = self.ids.spinner_eq.text
        tela.ids.spinner_tempo.text = self.ids.spinner_tm.text
        if self.popup_ref:
            self.popup_ref.dismiss()
        if hasattr(tela, 'iniciar_jogo'):
            Clock.schedule_once(lambda dt: tela.iniciar_jogo(), 0)

    def cancelar(self):
        if self.popup_ref:
            self.popup_ref.dismiss()

    def _show_error_popup(self, title, message):
        box = BoxLayout(orientation='vertical', spacing=10, padding=10)
        box.add_widget(Label(text=message))
        btn_ok = Button(text="OK", size_hint=(1, 0.2))
        box.add_widget(btn_ok)
        pop = Popup(title=title, content=box, size_hint=(0.6, 0.4))
        btn_ok.bind(on_release=pop.dismiss)
        pop.open()
        


from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior, DragBehavior
from kivy.uix.image import Image
from kivy.properties import StringProperty, BooleanProperty
from kivy.core.window import Window
import os

class HoverDraggableImageTextButton(DragBehavior, ButtonBehavior, RelativeLayout):
    source_normal = StringProperty('')
    source_hover = StringProperty('')
    source_down = StringProperty('')
    source = StringProperty('')
    text = StringProperty('')
    arrastavel = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.image = Image(allow_stretch=True, keep_ratio=False)
        self.label = Label(text=self.text, color=(1, 1, 1, 1), font_size='20sp', halign='center', valign='middle')

        self.add_widget(self.image)
        self.add_widget(self.label)

        # Quando o popup abre em cima do cursor, o Kivy pode aplicar hover/down
        # no botão novo sem um clique real. Este lock só libera hover depois
        # que o mouse sair da área inicial do botão.
        self._hover_locked_until_exit = False
        self._ignore_initial_touch = True
        Window.bind(mouse_pos=self.on_mouse_pos)
        self.update_sources()
        Clock.schedule_once(self.reset_visual_state, 0)
        Clock.schedule_once(self._prime_hover_lock, 0.02)

    def on_kv_post(self, base_widget):
        self.update_sources()
        Clock.schedule_once(self.reset_visual_state, 0)
        Clock.schedule_once(self._prime_hover_lock, 0.02)

    def update_sources(self):
        self.source_normal = self.source or self.source_normal
        if not self.source_hover:
            self.source_hover = self._add_suffix(self.source_normal, '_hover')
        if not self.source_down:
            self.source_down = self.source_hover
        self.image.source = self.source_normal
        self.label.text = self.text

    def _mouse_inside(self, pos=None):
        if not self.get_root_window():
            return False
        pos = pos or Window.mouse_pos
        return self.collide_point(*self.to_widget(*pos))

    def _prime_hover_lock(self, *args):
        self._hover_locked_until_exit = self._mouse_inside()
        self._ignore_initial_touch = self._hover_locked_until_exit
        self.image.source = self.source_normal

    def reset_visual_state(self, *args):
        self.state = 'normal'
        self.image.source = self.source_normal
        Clock.schedule_once(self._prime_hover_lock, 0)

    def _add_suffix(self, filename, suffix):
        name, ext = os.path.splitext(filename)
        return f"{name}{suffix}{ext}" if ext.lower() in ['.png', '.jpg', '.jpeg', '.webp'] else filename

    def on_mouse_pos(self, window, pos):
        # Botões de texto do popup não usam brilho por hover.
        # O glow só aparece durante o clique real.
        if not self.get_root_window():
            return

        if self.state != 'down':
            self.image.source = self.source_normal

        if self._hover_locked_until_exit and not self._mouse_inside(pos):
            self._hover_locked_until_exit = False
            self._ignore_initial_touch = False

    def on_touch_down(self, touch):
        # Ignora apenas o toque fantasma que pode vir junto com a abertura do popup.
        if self._ignore_initial_touch and self._mouse_inside(touch.pos):
            self.image.source = self.source_normal
            return False
        return super().on_touch_down(touch)

    def on_press(self):
        self._hover_locked_until_exit = False
        self._ignore_initial_touch = False
        if os.path.exists(self.source_down):
            self.image.source = self.source_down

    def on_release(self):
        self.image.source = self.source_normal
        self.state = 'normal'

from kivy.factory import Factory
Factory.register('HoverDraggableImageButton', cls=HoverDraggableImageButton)

Builder.load_string("""#:import resource_path_full introducao.resource_path_full

#:import dp kivy.metrics.dp

<CustomSpinnerOptionInicialintro@SpinnerOption>:
    background_normal: resource_path_full('botao generico iniciarintrodução.png', 'assets')
    background_down: resource_path_full('botao generico iniciarintrodução_hover.png', 'assets')
    color: 1, 1, 1, 1
    font_size: dp(20)

<ConfigMenu>:
    orientation: 'vertical'
    spacing: dp(25)
    padding: [dp(40), dp(40), dp(40), 0]  # padding: [ESQUERDA, TOPO, DIREITA, BASE]


    # Container de spinners (continua igual)
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(25)
        size_hint_y: None
        height: self.minimum_height

        DraggableSpinner:
            id: spinner_mode
            option_cls: 'CustomSpinnerOptionInicialintro'
            text: "Clique para escolher"
            font_size: dp(20)
            values: ['1º ano', '2º ano', '3º ano', 'Coffee Lovers']
            background_normal: resource_path_full('botao generico iniciarintrodução.png', 'assets')
            background_down: resource_path_full('botao generico iniciarintrodução_hover.png', 'assets')
            color: 1,1,1,1
            size_hint: None, None
            size: dp(600), dp(50)
            pos_hint: {"x": 0.28}  # <- aqui você move horizontalmente
           
            
        DraggableSpinner:
            id: spinner_eq
            option_cls: 'CustomSpinnerOptionInicialintro'
            text: "2"
            font_size: dp(20)
            values: [str(i) for i in range(2, 9)]
            background_normal: resource_path_full('botao generico iniciarintrodução.png', 'assets')
            background_down: resource_path_full('botao generico iniciarintrodução_hover.png', 'assets')
            color: 1,1,1,1
            size_hint: None, None
            size: dp(600), dp(50)
            pos_hint: {"x": 0.28}  # <- aqui você move horizontalmente
            

        DraggableSpinner:
            id: spinner_tm
            option_cls: 'CustomSpinnerOptionInicialintro'
            text: "1:00"
            font_size: dp(20)
            values: ['1:00', '1:30', '2:00', '2:30', '3:00', '3:30', '4:00', '4:30', '5:00']
            background_normal: resource_path_full('botao generico iniciarintrodução.png', 'assets')
            background_down: resource_path_full('botao generico iniciarintrodução_hover.png', 'assets')
            color: 1,1,1,1
            size_hint: None, None
            size: dp(600), dp(50)  # largura = 360, altura = 50

            pos_hint: {"x": 0.28}  # <- aqui você move horizontalmente
            

        Widget:

        BoxLayout:
            orientation: 'horizontal'
            spacing: dp(20)
            size_hint_y: None
            height: dp(60)
            padding: [0, 0, dp(180), 0]# padding: [ESQUERDA, TOPO, DIREITA, BASE]

            HoverDraggableImageTextButton:
                text: "Confirmar"
                size_hint_x: 0.5
                pos_hint: {"y": 0.30}# <- aqui você move verticalmente
                height: dp(50)
                source_normal: resource_path_full('botao generico iniciarintrodução.png', 'assets')
                source_hover: resource_path_full('botao generico iniciarintrodução_hover.png', 'assets')
                source_down: resource_path_full('botao generico iniciarintrodução_hover.png', 'assets')
                on_release: root.confirmar()

            HoverDraggableImageTextButton:
                text: "Cancelar"
                size_hint_x: 0.5
                pos_hint: {"y": 0.30}# <- aqui você move verticalmente
                height: dp(50)
                source_normal: resource_path_full('botao generico iniciarintrodução.png', 'assets')
                source_hover: resource_path_full('botao generico iniciarintrodução_hover.png', 'assets')
                source_down: resource_path_full('botao generico iniciarintrodução_hover.png', 'assets')
                on_release: root.cancelar()

<TelaIntroducao>:
    name: 'intro_screen'
    FloatLayout:

        Image:
            id: bg_image
            source: root.bg_source
            allow_stretch: True
            keep_ratio: False
            size_hint: 1, 1
            pos: self.parent.pos

        Video:
            id: intro_video
            source: root.video_source if root.video_enabled else ''
            state: 'play' if root.video_enabled else 'stop'
            opacity: 1 if root.video_enabled else 0
            on_eos: root.on_video_end()
            allow_stretch: True
            keep_ratio: False
            size_hint: 1, 1
            pos: self.parent.pos

        FloatLayout:
            id: main_content
            size_hint: 1, 1
            opacity: 0 if root.video_enabled else 1

            HoverDraggableImageButton:
                id: btn_config
                source: resource_path_full('configurar.png', 'assets')
                source_normal: resource_path_full('configurar.png', 'assets')
                source_hover: resource_path_full('configurar_hover.png', 'assets')
                source_down: resource_path_full('configurar_hover.png', 'assets')
                size_hint: None, None
                size: dp(288), dp(90)
                pos: root.get_button_pos('btn_config', 0.1, 0.1)
                on_release: root.manager.current = 'tela_inicial'

            HoverDraggableImageButton:
                id: btn_instrucoes
                source: resource_path_full('instruções.png', 'assets')
                source_normal: resource_path_full('instruções.png', 'assets')
                source_hover: resource_path_full('instruções_hover.png', 'assets')
                source_down: resource_path_full('instruções_hover.png', 'assets')
                size_hint: None, None
                size: dp(256), dp(80)
                pos: root.get_button_pos('btn_instrucoes', 0.35, 0.1)
                on_release: root.open_instructions_popup()

            HoverDraggableImageButton:
                id: btn_comecar
                source: resource_path_full('começar.png', 'assets')
                source_normal: resource_path_full('começar.png', 'assets')
                source_hover: resource_path_full('começar_hover.png', 'assets')
                source_down: resource_path_full('começar_hover.png', 'assets')
                size_hint: None, None
                size: dp(220), dp(60)
                pos: root.get_button_pos('btn_comecar', 0.4, 0.35)
                on_release: root.open_mode_popup()

            HoverDraggableImageButton:
                id: btn_creditos
                source: resource_path_full('créditos.png', 'assets')
                source_normal: resource_path_full('créditos.png', 'assets')
                source_hover: resource_path_full('créditos_hover.png', 'assets')
                source_down: resource_path_full('créditos_hover.png', 'assets')
                size_hint: None, None
                disabled: False
                size: dp(179.2), dp(56)
                pos: root.get_button_pos('btn_creditos', 0.7, 0.1)
                on_release: app.root.current = 'tela_creditos'
""")

class TelaIntroducao(Screen):
    video_source = StringProperty('')
    bg_source = StringProperty('')
    video_enabled = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.set_icon(resource_path_full('icone.ico', 'assets'))
        self.video_source = self.resource_path_full('introdução.mp4', 'assets')
        self.bg_source = self.resource_path_full('introdução cartoon.jpg', 'assets')
        self.video_enabled = bool(CoreVideoProvider and os.path.exists(self.video_source))
        Window.set_icon(resource_path_full('icone.ico', 'assets'))

    def salvar_todas_posicoes(self):
        botoes = ['btn_config', 'btn_instrucoes', 'btn_comecar', 'btn_creditos']
        data = {}
        for btn_id in botoes:
            if btn_id in self.ids:
                data[btn_id] = normalizar_posicao(self.ids[btn_id].pos)
        path = resource_path_full('posicoes_botoes.json', 'configs')
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print("[DEBUG] Todas as posições foram salvas manualmente.")

    def salvar_posicao_botao(self, btn_id, pos):
        path = resource_path_full('posicoes_botoes.json', 'configs')
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
        data[btn_id] = normalizar_posicao(pos)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"[DEBUG] JSON atualizado com {btn_id}: {data[btn_id]}")

    def on_pre_enter(self):
        print("[DEBUG] Entrou na TelaIntroducao")
        if not self.video_enabled:
            self.on_video_end()
        else:
            Clock.schedule_once(self._fallback_video_intro, 1.2)
        self.load_button_positions()

    def _fallback_video_intro(self, dt):
        """Evita tela branca se o provider de vídeo falhar silenciosamente."""
        try:
            video = self.ids.intro_video
            if self.ids.main_content.opacity == 0 and getattr(video, 'position', 0) == 0:
                self.on_video_end()
        except Exception:
            self.on_video_end()

    def load_button_positions(self):
        caminho = resource_path_full('posicoes_botoes.json', 'configs')
        print("[DEBUG] Entrou em load_button_positions")

        try:
            with open(caminho, "r", encoding="utf-8") as f:
                botoes = json.load(f)
            if "tela_intro" in botoes:
                botoes = botoes["tela_intro"]
            for btn_id, pos in botoes.items():
                if btn_id in self.ids:
                    self.ids[btn_id].pos = ajustar_posicao_letterbox(pos)
        except Exception as e:
            print(f"[ERRO] Falha ao carregar posições da tela_intro: {e}")

    def get_button_pos(self, btn_id, default_x, default_y):
        path = resource_path_full('posicoes_botoes.json', 'configs')
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "tela_intro" in data:
                data = data["tela_intro"]
            if btn_id in data:
                print(f"[DEBUG] Lendo posição salva para {btn_id}: {data[btn_id]}")
                return ajustar_posicao_letterbox(data[btn_id])
        largura_viewport, altura_viewport, offset_x, offset_y = calcular_viewport()
        print(f"[DEBUG] Posição padrão para {btn_id}: largura={Window.width}, altura={Window.height}")
        return [offset_x + largura_viewport * default_x, offset_y + altura_viewport * default_y]

    def on_video_end(self, *args):
        self.ids.intro_video.opacity = 0
        self.ids.main_content.opacity = 1

    def resource_path_full(self, rel_path, subfolder=""):
        return resource_path_full(rel_path, subfolder)

    def open_instructions_popup(self):
        img = Image(source=self.resource_path_full('cardinstruções.png', 'assets'), allow_stretch=True, keep_ratio=True)
        popup = Popup(
            content=img,
            size_hint=(None, None),
            size=(500, 700),
            title='',
            background=self.resource_path_full('fundotransparente.png', 'assets'),
            separator_height=0,
            auto_dismiss=True
        )
        popup.open()

    def open_mode_popup(self):
        popup = Popup(
            title='',
            size_hint=(0.9, 0.65),
            background=self.resource_path_full('iniciarintrodução.png', 'assets'),
            separator_height=0
        )

        # Criação do layout horizontal que alinha o menu à direita
        layout = BoxLayout(orientation='horizontal', padding=dp(20))

        # Espaço à esquerda (vazio)
        layout.add_widget(BoxLayout(size_hint=(0, 1)))  # ajuste conforme necessário

        # Menu real à direita
        config_menu = ConfigMenu()
        config_menu.popup_ref = popup
        layout.add_widget(config_menu)

        popup.content = layout
        popup.open()
        Clock.schedule_once(lambda dt: self._reset_popup_button_states(config_menu), 0)
        Clock.schedule_once(lambda dt: self._reset_popup_button_states(config_menu), 0.05)
        Clock.schedule_once(lambda dt: self._reset_popup_button_states(config_menu), 0.15)

    def _reset_popup_button_states(self, root_widget):
        for child in root_widget.walk():
            if hasattr(child, 'reset_visual_state'):
                child.reset_visual_state()

    def _show_error_popup(self, title, message):
        box = BoxLayout(orientation='vertical', spacing=10, padding=10)
        box.add_widget(Label(text=message))
        btn_ok = Button(text="OK", size_hint=(1, 0.2))
        box.add_widget(btn_ok)
        pop = Popup(title=title, content=box, size_hint=(0.6, 0.4))
        btn_ok.bind(on_release=pop.dismiss)
        pop.open()

    def ir_para_configuracoes(self):
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'tela_inicial'), 0.01)
