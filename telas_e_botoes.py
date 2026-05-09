import os
import sys
import datetime
os.environ['KIVY_AUDIO'] = 'ffpyplayer'
os.environ['KIVY_VIDEO'] = 'ffpyplayer'
os.environ['KIVY_IMAGE'] = 'sdl2'
from kivy.config import Config
Config.set('graphics', 'resizable', '1')  # impede redimensionamento
Config.set('graphics', 'width', '1366')
Config.set('graphics', 'height', '705')
Config.set('graphics', 'borderless', '0')  # janela com moldura
Config.set('graphics', 'fullscreen', '0')  # sem tela cheia
Config.set('graphics', 'show_cursor', '1')
Config.set('graphics', 'maxfps', '60')
Config.set('kivy', 'exit_on_escape', '1')

from kivy.core.window import Window
Window.minimum_width = 1366
Window.minimum_height = 705

Window.size = (1366, 705)
desired_size = (1366, 705)

def enforce_size(instance, width, height):
    """Garante que a janela continue no tamanho maximizado."""
    if (width, height) != desired_size:
        Window.size = desired_size

Window.bind(on_resize=enforce_size)
from kivy.core.window import Window
class Logger:
    def __init__(self, logfile_path):
        self.terminal_stdout = sys.stdout
        self.terminal_stderr = sys.stderr
        self.log = open(logfile_path, "a", encoding="utf-8")

    def write(self, message):
        self.terminal_stdout.write(message)  # escreve no terminal
        self.log.write(message)               # escreve no arquivo

    def flush(self):
        self.terminal_stdout.flush()
        self.log.flush()

# Criar pasta de logs
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

#  Nome do arquivo de log baseado na hora atual
log_filename = os.path.join(log_dir, f"log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt")



# Função para montar caminhos corretos
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


# ---- JSON cache helper ----
_JSON_CACHE = {}

def load_json_cached(path, encoding='utf-8', default=None):
    if path in _JSON_CACHE:
        return _JSON_CACHE[path]
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding=encoding) as f:
                data = json.load(f)
            _JSON_CACHE[path] = data
            return data
        except Exception as e:
            print(f'[JSONCache] Erro ao carregar {path}: {e}')
    return default
#  Definir base_path correto (se .exe, usa pasta do exe)
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.abspath(os.path.dirname(__file__))

Window.set_icon(resource_path_full('ícone roleta química.png', 'assets'))
import sys
import os
import datetime

class CustomLogger:
    def __init__(self, log_file_output, log_file_error, also_console=True):
        self.terminal_stdout = sys.stdout
        self.terminal_stderr = sys.stderr
        self.log_output = open(log_file_output, "a", encoding="utf-8")
        self.log_error = open(log_file_error, "a", encoding="utf-8")
        self.also_console = also_console

    def write(self, message):
        self.log_output.write(message)
        if self.also_console:
            self.terminal_stdout.write(message)

    def flush(self):
        self.log_output.flush()
        if self.also_console:
            self.terminal_stdout.flush()

    def write_error(self, message):
        self.log_error.write(message)
        if self.also_console:
            self.terminal_stderr.write(message)

    def flush_error(self):
        self.log_error.flush()
        if self.also_console:
            self.terminal_stderr.flush()

# Agora sim pode definir iniciar_logger()
def iniciar_logger():
    try:
        # Caminho base
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.abspath(os.path.dirname(__file__))

        # Criar pasta de logs
        log_dir = os.path.join(base_path, "logs")
        os.makedirs(log_dir, exist_ok=True)

        # Gerar nomes com timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_log_path = os.path.join(log_dir, f"log_output_{timestamp}.txt")
        error_log_path = os.path.join(log_dir, f"log_error_{timestamp}.txt")

        # Escrever cabeçalho inicial
        with open(output_log_path, "w", encoding="utf-8") as f_out:
            f_out.write(f"=== Iniciando execução: {timestamp} ===\n")
        with open(error_log_path, "w", encoding="utf-8") as f_err:
            f_err.write(f"=== Iniciando execução: {timestamp} ===\n")

        # Aplicar logger
        logger = CustomLogger(output_log_path, error_log_path, also_console=True)
        sys.stdout = logger
        sys.stderr = logger
        sys.stderr.write = logger.write_error
        sys.stderr.flush = logger.flush_error

        print(f"[LOG] Logger iniciado em {timestamp}")

    except Exception as e:
        print(f"[ERRO] Falha ao iniciar o logger: {e}")

# Chamar logger logo no início do programa
iniciar_logger()


import json
import random
from kivy.app import App
from kivy.config import Config
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from loading_screen import LoadingScreen

# ==== Histórico (logger simples) ====
import time as _time

def _hist_path():
    try:
        return resource_path_full('historico_log.jsonl', 'configs')
    except Exception:
        return os.path.join(os.path.abspath('.'), 'historico_log.jsonl')

# _hist_log removido - uso substituído pelo HistoryManager

# =====================================

try:
    # Opcional: se existir um módulo historico.py com tela própria
    from historico import HistoricoScreen
except Exception:
    HistoricoScreen = None
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.filechooser import FileChooserListView
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Ellipse
from kivy.uix.behaviors import DragBehavior, ButtonBehavior
from kivy.uix.slider import Slider
from kivy.factory import Factory
from kivy.uix.video import Video
import threading
# Seus módulos personalizados
from roda_animada import RotatingWheel
from introducao import TelaIntroducao
from predefinicoes import TelaPredefinicao
from loading_screen import LoadingScreen
from historico import HistoryManager
#from leitor_hover_tesseract import main as hover_loop
from creditos import TelaCreditos

# Resolução de referência original
############## Pega o tamanho real da tela física#########################################################################
#largura_tela_real, altura_tela_real = Window.system_size
# Printar os valores
#print(f"Largura real: {largura_tela_real}")
#print(f"Altura real: {altura_tela_real}")
largura_original = 1366
altura_original =705

# ======= VIEWPORT + LETTERBOX ADAPTATIVO =======

def mostrar_dica(self, dica_texto, dica_imagem=None):
    # Layout raiz com a mesma cara do resto
    root = BoxLayout(orientation='vertical', spacing=dp(12), padding=[dp(20), dp(14), dp(20), dp(14)])

    # Título custom dentro do conteúdo (já que o separator do Popup é zero)
    titulo_lbl = Label(
        text='Dica',
        size_hint_y=None, height=dp(28),
        font_size=dp(32),
        bold=True, color=(1,1,1,1),
        halign='left', valign='middle'
    )
    titulo_lbl.bind(size=lambda *_: setattr(titulo_lbl, 'text_size', (titulo_lbl.width, None)))
    root.add_widget(titulo_lbl)

    # Área rolável
    sc = ScrollView(size_hint=(1, 1))
    inner = BoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=None, padding=[0, 0, 0, 0])
    inner.bind(minimum_height=inner.setter('height'))

    # Texto da dica
    if dica_texto:
        dica_lbl = Label(
            text=dica_texto,
            color=(1,1,1,1),
            font_size=dp(22),
            halign='center', valign='top',
            size_hint_y=None
        )
        dica_lbl.bind(
            width=lambda *_: setattr(dica_lbl, 'text_size', (dica_lbl.width, None)),
            texture_size=lambda *_: setattr(dica_lbl, 'height', dica_lbl.texture_size[1])
        )
        inner.add_widget(dica_lbl)

    # Imagem da dica com TAMANHO LIMITADO (para não ficar gigante)
    if dica_imagem:
        img = Image(source=dica_imagem, allow_stretch=True, keep_ratio=True, size_hint_y=None)

        # Limite de altura (ex.: 260dp) e ajuste proporcional de largura
        MAX_H = dp(300)

        def _fit_img(*_):
            if img.texture:
                # calcula altura proporcional à largura disponível, mas não passa de MAX_H
                avail_w = inner.width
                if img.texture_size[0] == 0:
                    return
                ideal_h = avail_w * img.texture_size[1] / img.texture_size[0]
                h = min(ideal_h, MAX_H)
                # ajusta largura conforme a altura que coube
                w = h * img.texture_size[0] / img.texture_size[1]
                img.size = (w, h)

        inner.bind(width=_fit_img)
        img.bind(texture=_fit_img)
        inner.add_widget(img)

    sc.add_widget(inner)
    root.add_widget(sc)

    # Botão fechar com o mesmo visual
    btn_fechar = Button(
        text='Fechar',
        size_hint_y=None, height=dp(48),
        font_size=dp(20), color=(1,1,1,1),
        background_normal=resource_path_full('botao generico popup generico.png', 'assets'),
        background_down=resource_path_full('botao generico popup generico.png', 'assets')
    )
    root.add_widget(btn_fechar)

    popup = Popup(
        title='',
        title_size=0,
        separator_height=0,
        content=root,
        size_hint=(0.8, 0.8),
        background=resource_path_full('popup genérico HD.png', 'assets'),
        background_color=(1,1,1,1)
    )
    btn_fechar.bind(on_release=lambda *_: popup.dismiss())
    popup.open()
def calcular_viewport():
    aspect_ratio_original = largura_original / altura_original
    aspect_ratio_tela = Window.width / Window.height

    if aspect_ratio_tela > aspect_ratio_original:
        # Tela mais larga
        altura_viewport = Window.height
        largura_viewport = altura_viewport * aspect_ratio_original
    else:
        # Tela mais alta
        largura_viewport = Window.width
        altura_viewport = largura_viewport / aspect_ratio_original

    offset_x = (Window.width - largura_viewport) / 2
    offset_y = (Window.height - altura_viewport) / 2

    return largura_viewport, altura_viewport, offset_x, offset_y

def ajustar_posicao_letterbox(posicao_salva):
    largura_viewport, altura_viewport, offset_x, offset_y = calcular_viewport()

    x_novo = posicao_salva[0] * (largura_viewport / largura_original) + offset_x
    y_novo = posicao_salva[1] * (altura_viewport / altura_original) + offset_y

    return [x_novo, y_novo]
# ================================================
###########################################################################################################################
# Pares de arquivos: (referência, destino real)
arquivos_posicoes = [
    (resource_path_full("posicoes_botoes_inicial - original.json", "configs"), resource_path_full("posicoes_botoes_inicial.json", "configs")),
    (resource_path_full("posicoes_botoes_listar - original.json", "configs"), resource_path_full("posicoes_botoes_listar.json", "configs")),
    (resource_path_full("posicoes_predefinicoes - original.json", "configs"), resource_path_full("posicoes_predefinicoes.json", "configs")),
    (resource_path_full("posicoes_botoes - original.json", "configs"), resource_path_full("posicoes_botoes.json", "configs")),
    (resource_path_full("posicoes_botoes_fake - original.json", "configs"), resource_path_full("posicoes_botoes_fake.json", "configs")),
]

def carregar_posicoes(tela, caminho_json):
    import json
    import os
    from kivy.core.window import Window

    if os.path.exists(caminho_json):
        with open(caminho_json, 'r', encoding='utf-8') as f:
            posicoes = json.load(f)
            for btn_id, pos in posicoes.items():
                try:
                    widget = tela.ids.get(btn_id)
                    if widget:
                        print(f"[DEBUG] Aplicando posição {btn_id}: {pos}")
                        widget.pos = pos
                except Exception as e:
                    print(f"[ERRO] Erro ao aplicar posição do botão '{btn_id}': {e}")
    else:
        print(f"[AVISO] Arquivo de posições '{caminho_json}' não encontrado.")

def ajustar_posicoes_para_tela():
    """Atualiza todos os arquivos de posição reais com base nos arquivos de referência."""
    for arquivo_original, arquivo_destino in arquivos_posicoes:
        if not os.path.exists(arquivo_original):
            print(f"Arquivo de referência não encontrado: {arquivo_original}")
            continue

        with open(arquivo_original, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        novos_dados = {id_botao: ajustar_posicao_letterbox(posicao) for id_botao, posicao in dados.items()}

        with open(arquivo_destino, 'w', encoding='utf-8') as f:
            json.dump(novos_dados, f, indent=4, ensure_ascii=False)

        print(f"Ajustado e salvo: {arquivo_destino}")

class ImageButton(ButtonBehavior, Image):
    """Botão com imagem, clicável."""
    pass

    def carregar_posicoes(widget_root, arquivo_json):
        """Carrega as posições dos botões e ajusta conforme a tela atual."""
        if os.path.exists(arquivo_json):
            with open(arquivo_json, "r", encoding="utf-8") as f:
                posicoes = json.load(f)
            for btn_id, posicao in posicoes.items():
                if btn_id in widget_root.ids:
                    widget_root.ids[btn_id].pos = ajustar_posicao_letterbox(posicao)

    def salvar_posicoes(widget_root, arquivo_json):
        """Salva a posição atual dos botões em relação ao tamanho original (1366x705)."""
        largura_viewport, altura_viewport, offset_x, offset_y = calcular_viewport()

        posicoes = {}
        for btn_id, widget in widget_root.ids.items():
            if hasattr(widget, 'pos'):
                x_prop = (widget.x - offset_x) * (largura_original / largura_viewport)
                y_prop = (widget.y - offset_y) * (altura_original / altura_viewport)
                posicoes[btn_id] = [x_prop, y_prop]

        with open(arquivo_json, "w", encoding="utf-8") as f:
            json.dump(posicoes, f, indent=4, ensure_ascii=False)


class HoverDraggableSpinner(DragBehavior, Spinner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drag_rectangle = [0, 0, 100, 100]
        self.drag_timeout = 10000000
        self.drag_distance = 0
        self._drag_enabled = False

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            tela = self.get_root_window().children[0]
            if hasattr(tela, 'arraste_liberado'):
                self._drag_enabled = tela.arraste_liberado
            else:
                self._drag_enabled = False

            if self._drag_enabled:
                # Se arrastar está liberado, arrasta
                return super(DragBehavior, self).on_touch_down(touch)
            else:
                # Se arrastar NÃO está liberado, abre o spinner normalmente
                return super(Spinner, self).on_touch_down(touch)
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._drag_enabled:
            return super().on_touch_move(touch)
        return False

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            tela = self.get_root_window().children[0]
            if hasattr(tela, 'salvar_posicao_botao'):
                for id_name, widget in self.parent.ids.items():
                    if widget is self:
                        tela.salvar_posicao_botao(id_name, self.pos)
                        break
        return super().on_touch_up(touch)

# Widget personalizado: Botão Circular
class CircularButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Remove as imagens padrão para usar nosso desenho circular
        self.background_normal = ''
        self.background_down = ''
        # Define uma cor de fundo padrão; você pode personalizar
        self.background_color = (0.7, 0.7, 0.7, 1)
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.background_color)
            Ellipse(pos=self.pos, size=self.size)
# Função para retornar o nome do arquivo de dados conforme o modo de jogo
def get_db_filename(game_mode):
    if game_mode in ["1º ano", "1 ano"]:
        return resource_path_full('dataperguntas1ano_bncc.json', 'configs')
    elif game_mode in ["2º ano", "2 ano"]:
        return resource_path_full('dataperguntas2ano_bncc.json', 'configs')
    elif game_mode in ["3º ano", "3 ano"]:
        return resource_path_full('dataperguntas3ano_bncc.json', 'configs')
    elif game_mode == "Coffee Lovers":
        return resource_path_full('dataperguntas_coffeelovers.json', 'configs')
    else:
        return resource_path_full('dataperguntas_coffeelovers.json', 'configs')

# Lista de opções de tempo (1 min até 5 min, de 30 em 30s):
TEMPOS_DISPONIVEIS = [
    '1:00', '1:30', '2:00', '2:30',
    '3:00', '3:30', '4:00', '4:30',
    '5:00'
]
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
        font_size =dp(20),
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
        background = resource_path_full('popup genérico HD.png', 'assets'),
        background_color=(1, 1, 1, 1),
        content=content,
        size_hint=(0.6, 0.4)
    )

    ok_button.bind(on_press=lambda *args: popup.dismiss())
    popup.open()
    return popup

class HoverDraggableImageButton(DragBehavior, ButtonBehavior, Image):
    source_normal = StringProperty('')
    source_hover = StringProperty('')
    source_down = StringProperty('')
    arrastavel = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use o valor de self.source diretamente
        self.source_normal = self.source
        self.source_hover = self._add_suffix(self.source_normal, '_hover')
        self.source_down = self._add_suffix(self.source_normal, '_down')
        self._has_hover = os.path.exists(self.source_hover)
        self._has_down = os.path.exists(self.source_down)
        Window.bind(mouse_pos=self.on_mouse_pos)
        # cache existence flags to avoid disk checks every mouse move
        self._has_hover = os.path.exists(self.source_hover)
        self._has_down = os.path.exists(self.source_down)




    def on_kv_post(self, base_widget):
        self.source_normal = self.source
        self.source_hover = self._add_suffix(self.source_normal, '_hover')
        self.source_down = self._add_suffix(self.source_normal, '_down')
        self.source = self.source_normal
 

    def _add_suffix(self, filename, suffix):
        name, ext = os.path.splitext(filename)
        return f"{name}{suffix}{ext}" if ext.lower() in ['.png', '.jpg', '.jpeg', '.webp'] else filename

    def on_mouse_pos(self, window, pos):
        if not self.get_root_window():
            return
        inside = self.collide_point(*self.to_widget(*pos))
        if inside and self._has_hover:
            self.source = self.source_hover
        else:
            self.source = self.source_normal


from kivy.factory import Factory
Factory.register('HoverDraggableImageButton', cls=HoverDraggableImageButton)
Builder.load_string('''#:import resource_path_full telas_e_botoes.resource_path_full

<ImageButtonEditar@ButtonBehavior+Image>:
    source: resource_path_full('botao generico listarperguntaseditar.png', 'assets')
    background_down: resource_path_full('botao generico listarperguntaseditar_hover.png', 'assets')
    allow_stretch: False
    keep_ratio: True
    size_hint_x: None
    width: dp(120)

<CustomSpinnerOptionInicial@SpinnerOption>:
    background_normal: resource_path_full('botao generico telainicial.png', 'assets')
    background_down: resource_path_full('botao generico telainicial_hover.png', 'assets')
    color: 1, 1, 1, 1
    font_size: dp(20)

<CustomSpinnerOptionListar@SpinnerOption>:
    background_normal: resource_path_full('botao generico listarperguntas.png', 'assets')
    background_down: resource_path_full('botao generico listarperguntas_hover.png', 'assets')
    color: 1, 1, 1, 1
    font_size: dp(20)
<TextoComBorda@FloatLayout>:
    texto: ''
    font_size: dp(25)
    cor_texto: 1, 0, 0, 1  # vermelho
    cor_borda: 1, 1, 1, 1  # branco
    size_hint: None, None
    size: dp(200), dp(40)
    pos_hint: {"center_x": 0.5, "center_y": 0.39}
    opacity: 1

    # Labels da borda (5 ao redor)
    Label:
        text: root.texto
        font_size: root.font_size
        color: root.cor_borda
        pos_hint: {"center_x": 0.492, "center_y": 0.38}
    Label:
        text: root.texto
        font_size: root.font_size
        color: root.cor_borda
        pos_hint: {"center_x": 0.500, "center_y": 0.37}
    Label:
        text: root.texto
        font_size: root.font_size
        color: root.cor_borda
        pos_hint: {"center_x": 0.486, "center_y": 0.38}
    Label:
        text: root.texto
        font_size: root.font_size
        color: root.cor_borda
        pos_hint: {"center_x": 0.480, "center_y": 0.38}
    Label:
        text: root.texto
        font_size: root.font_size
        color: root.cor_borda
        pos_hint: {"center_x": 0.5, "center_y": 0.37}

    # Texto principal
    Label:
        text: root.texto
        font_size: root.font_size
        color: root.cor_texto
        pos_hint: {"center_x": 0.5, "center_y": 0.38}

    
<VideoScreen>:
    Video:
        id: video
        source: root.video_path
        state: 'stop'
        size_hint: (1, 1)
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        allow_stretch: True
        keep_ratio: False
        options: {'eos': 'stop'}
        on_eos: root.on_video_end(self, self.state)

<TelaJogo>:
    FloatLayout:
        Image:
            source: resource_path_full('xicara de cima.png', 'assets')
            allow_stretch: True
            keep_ratio: True
            size_hint: 1, 1
            pos_hint: {"center_x": 0.5, "center_y": 0.5}

        BoxLayout:
            orientation: 'vertical'
            padding: dp(10)
            spacing: dp(10)
            size_hint: 1, 1

            BoxLayout:
                id: scoreboard_layout
                orientation: 'horizontal'
                size_hint_y: 0.1
                padding: dp(10)
                spacing: dp(10)

            Widget:
                size_hint_y: 0.06

            FloatLayout:
                size_hint_y: 0.5
                pos_hint: {"center_x": 0.5, "center_y": 0.5}

                RotatingWheel:
                    id: rotating_wheel
                    size_hint: 1.2, 1.2
                    pos_hint: {"center_x": 0.5, "center_y": 0.5}

                HoverDraggableImageButton:
                    source: resource_path_full("botao_girar.png", 'assets')
                    source_normal: resource_path_full('botao_girar.png', 'assets')
                    source_hover: resource_path_full('botao_girar_hover.png', 'assets')
                    source_down: resource_path_full('botao_girar_hover.png', 'assets')
                    size_hint: None, None
                    size: dp(100), dp(100)
                    pos_hint: {"center_x": 0.5, "center_y": 0.5}
                    on_press:
                        root.girar_roda()
                        root.ids.instrucao_overlay.opacity = 0

                HoverDraggableImageButton:
                    source: resource_path_full('setavoltar.png', 'assets')
                    source_normal: resource_path_full('setavoltar.png', 'assets')
                    source_hover: resource_path_full('setavoltar_hover.png', 'assets')
                    source_down: resource_path_full('setavoltar_hover.png', 'assets')
                    size_hint: 0.2, 0.2
                    pos_hint: {"left": 1, "top": 1}
                    on_release: root.encerrar_jogo()

            Widget:
                size_hint_y: 0.1

    # === SOBREPOSIÇÃO DE INSTRUÇÃO COM FUNDO ESCURO ===
    FloatLayout:
        id: instrucao_overlay
        opacity: 1  # tudo aqui some junto
        canvas.before:
            Color:
                rgba: 0, 0, 0, 0.8  # fundo preto semi-transparente
            Rectangle:
                pos: self.pos
                size: self.size

        Image:
            id: seta_instrucao
            source: resource_path_full("setadica.png", 'assets')
            size_hint: None, None
            size: dp(100), dp(100)
            pos_hint: {"center_x": 0.57, "center_y": 0.49}

        TextoComBorda:
            id: texto_instrucao
            texto: "Clique para girar"
            pos_hint: {"center_x": 0.5, "center_y": 0.38}

        HoverDraggableImageButton:
            source: resource_path_full("botao_girar.png", 'assets')
            source_normal: resource_path_full('botao_girar.png', 'assets')
            source_hover: resource_path_full('botao_girar_hover.png', 'assets')
            source_down: resource_path_full('botao_girar_hover.png', 'assets')
            size_hint: None, None
            size: dp(100), dp(100)
            pos_hint: {"center_x": 0.5, "center_y": 0.45}
            on_press:
                root.girar_roda()
                root.ids.instrucao_overlay.opacity = 0

<TelaInicial>:
    name: 'tela_inicial'

    FloatLayout:
        Image:
            source: resource_path_full('telainicial.png', 'assets')
            allow_stretch: True
            keep_ratio: False
            size_hint: None, None
            size: root.viewport_size
            pos: root.bg_pos

        FloatLayout:
            id: botoes_layout

            HoverDraggableSpinner:
                id: spinner_game_mode
                option_cls: 'CustomSpinnerOptionInicial'
                text: 'Clique para escolher'
                font_size: dp(19)
                values: ['1º ano', '2º ano', '3º ano', 'Coffee Lovers']
                background_normal: resource_path_full('botao generico telainicial.png', 'assets')
                background_down: resource_path_full('botao generico telainicial_hover.png', 'assets')
                color: 1,1,1,1
                size_hint: None, None
                size: dp(180), dp(80)
                pos: root.get_button_pos('spinner_game_mode', 0.3, 0.8)

            HoverDraggableSpinner:
                id: spinner_equipes
                option_cls: 'CustomSpinnerOptionInicial'
                text: '2'
                font_size: dp(20)
                values: ['2','3','4','5','6','7','8']
                background_normal: resource_path_full('botao generico telainicial.png', 'assets')
                background_down: resource_path_full('botao generico telainicial_hover.png', 'assets')
                color: 1,1,1,1
                size_hint: None, None
                size: dp(180), dp(80)
                pos: root.get_button_pos('spinner_equipes', 0.7, 0.8)

            HoverDraggableSpinner:
                id: spinner_predefinicao
                option_cls: 'CustomSpinnerOptionInicial'
                text: 'Escolher Predefinição'
                font_size: dp(20)
                values: root.predef_names
                background_normal: resource_path_full('botao generico telainicial.png', 'assets')
                background_down: resource_path_full('botao generico telainicial_hover.png', 'assets')
                size_hint: None, None
                size: dp(250), dp(60)
                pos: root.get_button_pos('spinner_predefinicao', 0.5, 0.9)
                on_text: root.popup_configurar_predefinicao(self.text)

            HoverDraggableSpinner:
                id: spinner_tempo
                option_cls: 'CustomSpinnerOptionInicial'
                text: '1:00'
                font_size: dp(20)
                values: root.tempos_disponiveis
                background_normal: resource_path_full('botao generico telainicial.png', 'assets')
                background_down: resource_path_full('botao generico telainicial_hover.png', 'assets')
                color: 1,1,1,1
                size_hint: None, None
                size: dp(180), dp(80)
                pos: root.get_button_pos('spinner_tempo', 0.5, 0.7)

            HoverDraggableImageButton:
                id: btn_iniciar
                source_normal: resource_path_full('iniciar jogo.png', 'assets')
                source_hover: resource_path_full('iniciar jogo_hover.png', 'assets')
                source_down: resource_path_full('iniciar jogo_hover.png', 'assets')
                source: resource_path_full('iniciar jogo.png', 'assets')
                size_hint: None, None
                size: dp(237.5), dp(95)
                pos: root.get_button_pos('btn_iniciar', 0.4, 0.6)
                on_release: root.iniciar_jogo()

            HoverDraggableImageButton:
                id: btn_volume
                source_normal: resource_path_full('volume.png', 'assets')
                source_hover: resource_path_full('volume_hover.png', 'assets')
                source_down: resource_path_full('volume_hover.png', 'assets')
                source: resource_path_full('volume.png', 'assets')
                size_hint: None, None
                size: dp(90), dp(90)
                pos: root.get_button_pos('btn_volume', 0.85, 0.85)
                on_release: root.abrir_popup_volume()

            HoverDraggableImageButton:
                id: btn_adicionar
                source_normal: resource_path_full('adicionar perguntas.png', 'assets')
                source_hover: resource_path_full('adicionar perguntas_hover.png', 'assets')
                source_down: resource_path_full('adicionar perguntas_hover.png', 'assets')
                source: resource_path_full('adicionar perguntas.png', 'assets')
                size_hint: None, None
                size: dp(237.5), dp(95)
                pos: root.get_button_pos('btn_adicionar', 0.4, 0.5)
                on_release: root.manager.current = 'add_edit_question'

            HoverDraggableImageButton:
                id: btn_listar
                source_normal: resource_path_full('listar perguntas.png', 'assets')
                source_hover: resource_path_full('listar perguntas_hover.png', 'assets')
                source_down: resource_path_full('listar perguntas_hover.png', 'assets')
                source: resource_path_full('listar perguntas.png', 'assets')
                size_hint: None, None
                size: dp(237.5), dp(95)
                pos: root.get_button_pos('btn_listar', 0.4, 0.4)
                on_release: root.abrir_com_preload('question_list')

            HoverDraggableImageButton:
                id: btn_voltar
                source_normal: resource_path_full('setavoltar.png', 'assets')
                source_hover: resource_path_full('setavoltar_hover.png', 'assets')
                source_down: resource_path_full('setavoltar_hover.png', 'assets')
                source: resource_path_full('setavoltar.png', 'assets')
                size_hint: None, None
                size: dp(180), dp(80)
                pos: root.get_button_pos('btn_voltar', 0.02, 0.88)
                on_release: root.manager.current = 'intro_screen'

            HoverDraggableImageButton:
                id: btn_predefinicoes
                source_normal: resource_path_full('predefinições.png', 'assets')
                source_hover: resource_path_full('predefinições_hover.png', 'assets')
                source_down: resource_path_full('predefinições_hover.png', 'assets')
                source: resource_path_full('predefinições.png', 'assets')
                size_hint: None, None
                size: dp(237.5), dp(95)
                pos: root.get_button_pos('btn_predefinicoes', 0.4, 0.3)
                on_release: root.abrir_com_preload('tela_predefinicao')
            HoverDraggableImageButton:
                id: btn_historico
                source_normal: resource_path_full('historico.png', 'assets')
                source_hover: resource_path_full('historico_hover.png', 'assets')
                source_down: resource_path_full('historico_hover.png', 'assets')
                source: resource_path_full('historico.png', 'assets')
                size_hint: None, None
                size: dp(237.5), dp(95)
                pos: root.get_button_pos('btn_historico', 0.4, 0.2)
                on_release:
                    root.abrir_com_preload('historico_screen') if hasattr(root, 'abrir_com_preload') else setattr(root.manager, 'current', 'historico_screen')


<AddEditQuestionScreen>:
    name: 'add_edit_question'
    game_mode: 'Coffee Lovers'
    
    FloatLayout:
        Image:
            source: resource_path_full('fundo generico.jpg', 'assets')  # Caminho para sua imagem
            allow_stretch: True
            keep_ratio: False
            size_hint: 1, 1
            pos_hint: {"x": 0, "y": 0}
            
    ScrollView:
        do_scroll_x: False
        BoxLayout:
            orientation: 'vertical'
            spacing: dp(10)
            padding: dp(10)
            size_hint_y: None
            height: self.minimum_height
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(40)
                Label:
                    text: 'Modo de Jogo:'
                    font_size: dp(20)
                    size_hint_x: 0.2
                Spinner:
                    id: spinner_game_mode_edit
                    option_cls: 'CustomSpinnerOptionListar'
                    background_normal: resource_path_full('botao generico listarperguntas.png', 'assets')
                    background_down: resource_path_full('botao generico listarperguntas_hover.png', 'assets')
                    text: root.game_mode
                    size_hint_x: 0.5
                    font_size: dp(20)
                    values: ['1º ano', '2º ano', '3º ano', 'Coffee Lovers']
                    on_text:
                        root.game_mode = self.text
                        root.carregar_areas_existentes()
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(40)
                Label:
                    text: 'Área:'
                    size_hint_x: 0.3
                    font_size: dp(20)
                Spinner:
                    id: area_spinner
                    option_cls: 'CustomSpinnerOptionListar'
                    text: 'Selecione uma Área'
                    background_normal: resource_path_full('botao generico listarperguntas.png', 'assets')
                    background_down: resource_path_full('botao generico listarperguntas_hover.png', 'assets')
                    font_size: dp(20)
                    size_hint_x: 0.7
                    font_size: self.height * 0.5
                    values: root.available_areas
                    on_text: root.selecionar_area(self.text)
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(40)
                Label:
                    text: 'Nova Área:'
                    size_hint_x: 0.3
                    font_size: dp(20)
                TextInput:
                    id: nova_area
                    size_hint_x: 0.5
                    font_size: dp(20)
                    multiline: False
                HoverDraggableImageTextButton:
                    text: 'Adicionar'
                    size_hint_x: 0.2
                    font_size: dp(20)
                    source: resource_path_full('botao generico listarperguntas.png', 'assets')
                    source_normal: resource_path_full('botao generico listarperguntas.png', 'assets')
                    source_hover: resource_path_full('botao generico listarperguntas_hover.png', 'assets')
                    source_down: resource_path_full('botao generico listarperguntas_hover.png', 'assets')
                    on_press: root.adicionar_area()
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(40)
                Label:
                    text: 'Pergunta:'
                    font_size: dp(20)
                    size_hint_x: 0.3
                    font_size: dp(20)
                TextInput:
                    id: pergunta
                    size_hint_x: 0.7
                    font_size: dp(20)
                    multiline: False
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(40)
                Label:
                    text: 'Alternativa 0:'
                    size_hint_x: 0.3
                    font_size: dp(20)
                TextInput:
                    id: alternativa1
                    size_hint_x: 0.7
                    font_size: dp(20)
                    multiline: False
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(40)
                Label:
                    text: 'Alternativa 1:'
                    size_hint_x: 0.3
                    font_size: self.height * 0.5
                TextInput:
                    id: alternativa2
                    size_hint_x: 0.7
                    font_size: self.height * 0.5
                    multiline: False
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(40)
                Label:
                    text: 'Alternativa 2:'
                    size_hint_x: 0.3
                    font_size: self.height * 0.5
                TextInput:
                    id: alternativa3
                    size_hint_x: 0.7
                    font_size: self.height * 0.5
                    multiline: False
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(40)
                Label:
                    text: 'Alternativa 3:'
                    size_hint_x: 0.3
                    font_size: self.height * 0.5
                TextInput:
                    id: alternativa4
                    size_hint_x: 0.7
                    font_size: self.height * 0.5
                    multiline: False
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(40)
                Label:
                    text: 'Resposta Correta (0-3):'
                    size_hint_x: 0.3
                    font_size: self.height * 0.5
                TextInput:
                    id: resposta_correta
                    size_hint_x: 0.7
                    font_size: self.height * 0.5
                    multiline: False
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(40)
                Label:
                    text: 'Dificuldade:'
                    size_hint_x: 0.3
                    font_size: self.height * 0.5
                Spinner:
                    id: dificuldade
                    option_cls: 'CustomSpinnerOptionListar'
                    background_normal: resource_path_full('botao generico listarperguntas.png', 'assets')
                    background_down: resource_path_full('botao generico listarperguntas_hover.png', 'assets')
                    text: 'Fácil'
                    size_hint_x: 0.7
                    font_size: self.height * 0.5
                    values: ['Fácil', 'Médio', 'Difícil']
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(40)
                Label:
                    text: 'Cor da Área:'
                    size_hint_x: 0.3
                    font_size: self.height * 0.5
                HoverDraggableImageButton:
                    id: escolher_cor
                    background_normal: resource_path_full('botao generico listarperguntas.png', 'assets')
                    background_down: resource_path_full('botao generico listarperguntas_hover.png', 'assets')
                    text: 'Escolher Cor'
                    size_hint_x: 0.7
                    font_size: self.height * 0.5
                    background_color: root.cor_selecionada
                    on_press: root.mostrar_seletor_cor()
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(40)
                Label:
                    text: 'Dica (Texto):'
                    size_hint_x: 0.3
                    font_size: self.height * 0.5
                TextInput:
                    id: dica_texto
                    size_hint_x: 0.7
                    font_size: self.height * 0.5
                    multiline: False
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(40)
                Label:
                    text: 'Caminho da Imagem:'
                    size_hint_x: 0.3
                    font_size: self.height * 0.5
                TextInput:
                    id: dica_imagem
                    size_hint_x: 0.5
                    font_size: self.height * 0.5
                    multiline: False
                HoverDraggableImageTextButton:
                    source_normal: resource_path_full('botao generico listarperguntas.png', 'assets')
                    surce_down: 'botao generico listarperguntas_hover.png'
                    source_hover: resource_path_full('botao generico listarperguntas_hover.png', 'assets')
                    source: resource_path_full('botao generico listarperguntas.png', 'assets')
                    text: 'Escolher Arquivo'
                    size_hint_x: 0.2
                    font_size: self.height * 0.5
                    on_press: root.abrir_filechooser()
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(40)
                Button:
                    background_normal: resource_path_full('botao generico listarperguntas.png', 'assets')
                    background_down: resource_path_full('botao generico listarperguntas_hover.png', 'assets')
                    text: 'Salvar'
                    font_size: self.height * 0.5
                    on_press: root.salvar_pergunta()
                HoverDraggableImageTextButton:
                    source: resource_path_full('botao generico listarperguntas.png', 'assets')
                    source_down: resource_path_full('botao generico listarperguntas_hover.png', 'assets')
                    source_normal: resource_path_full('botao generico listarperguntas.png', 'assets')
                    source_hover: resource_path_full('botao generico listarperguntas_hover.png', 'assets')
                    text: 'Cancelar'
                    font_size: self.height * 0.5
                    on_press: root.cancelar_pergunta()

<QuestionListScreen>:
    canvas.before:
        Color:
            rgba: app.cor_fundo
        Rectangle:
            pos: self.pos
            size: self.size
    game_mode: 'Coffee Lovers'

    FloatLayout:
        Image:
            source: resource_path_full('listarperguntas.jpg', 'assets')
            allow_stretch: True
            keep_ratio: False
            size_hint: 1, 1

        DraggableSpinner:
            id: spinner_game_mode_list
            option_cls: 'CustomSpinnerOptionListar'
            text: root.game_mode
            font_size: dp(20)
            values: ['1º ano', '2º ano', '3º ano', 'Coffee Lovers']
            background_normal: resource_path_full('botao generico listarperguntas.png', 'assets')
            background_down: resource_path_full('botao generico listarperguntas_hover.png', 'assets')
            color: 1, 1, 1, 1
            size_hint: None, None
            size: dp(180), dp(80)
            pos: root.get_button_pos('spinner_game_mode_list', 0.35, 0.87)
            on_text:
                root.game_mode = self.text
                root.carregar_areas()
                root.carregar_perguntas()

        HoverDraggableImageButton:
            id: btn_voltar_listar
            source_normal: resource_path_full('setavoltar.png', 'assets')
            source_hover: resource_path_full('setavoltar_hover.png', 'assets')
            source_down: resource_path_full('setavoltar_hover.png', 'assets')
            source: resource_path_full('setavoltar.png', 'assets')
            size_hint: None, None
            size: dp(180), dp(80)
            pos: root.get_button_pos('btn_voltar_listar', 0.4, 0.78)
            on_release: root.manager.current = 'tela_inicial'

        DraggableSpinner:
            id: spinner_area_filter
            option_cls: 'CustomSpinnerOptionListar'
            text: 'Todas'
            font_size: dp(20)
            values: ['Todas'] + root.available_areas
            background_normal: resource_path_full('botao generico listarperguntas.png', 'assets')
            background_down: resource_path_full('botao generico listarperguntas_hover.png', 'assets')
            color: 1, 1, 1, 1
            size_hint: None, None
            size: dp(180), dp(80)
            pos: root.get_button_pos('spinner_area_filter', 0.2, 0.68)
            on_text: root.apply_filters()

        DraggableSpinner:
            id: spinner_difficulty_filter
            option_cls: 'CustomSpinnerOptionListar'
            text: 'Todas'
            font_size: dp(20)
            values: ['Todas'] + root.available_difficulties

            background_normal: resource_path_full('botao generico listarperguntas.png', 'assets')
            background_down: resource_path_full('botao generico listarperguntas_hover.png', 'assets')
            color: 1, 1, 1, 1
            size_hint: None, None
            size: dp(180), dp(80)
            pos: root.get_button_pos('spinner_difficulty_filter', 0.6, 0.68)
            on_text: root.apply_filters()

        ScrollView:
            size_hint: 1, 0.25  # ← Menor altura
            pos_hint: {"x": 0, "y": 0.25}  # ← Um pouco mais alto
            BoxLayout:
                id: question_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(10)
                font_size: dp(20)

''')
class TelaInicial(Screen):
    viewport_size = ListProperty([1366, 705])
    bg_pos = ListProperty([0, 0])

    def atualizar_layout_resize(self, *args):
        # Recalcula viewport
        largura_viewport, altura_viewport, offset_x, offset_y = calcular_viewport()
        self.viewport_size = [largura_viewport, altura_viewport]
        self.bg_pos = [offset_x, offset_y]
        # Recarrega posições dos botões
        Clock.schedule_once(lambda dt: self.load_button_positions(), 0)

    def on_enter(self, *args):
        super().on_enter(*args)
        Window.bind(on_resize=self.atualizar_layout_resize)
        self.atualizar_layout_resize()

    def on_leave(self, *args):
        super().on_leave(*args)
        Window.unbind(on_resize=self.atualizar_layout_resize)

    def configurar_modo_dev(self):
        from kivy.core.window import Window
        def teclado_dev(window, key, scancode, codepoint, modifiers):
            if key == 100 and 'ctrl' in modifiers and 'shift' in modifiers:  # Ctrl + Shift + D
                self.abrir_menu_dev()

        Window.bind(on_key_down=teclado_dev)

    def abrir_menu_dev(self):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        # Aqui você pode adicionar os widgets do menu dev no BoxLayout "content"

    def abrir_com_preload(self, target_name):
        app = App.get_running_app()
        app.loading_request = {'target': target_name}
        self.manager.current = 'loading_screen'

        
    def calcular_posicao_fundo(self):
        largura_viewport, altura_viewport, offset_x, offset_y = calcular_viewport()
        return offset_x, offset_y

    def ir_para_tela(self, nome_tela):
        self.manager.current = nome_tela
        if hasattr(self, 'popup_dev'):
            self.popup_dev.dismiss()

    def salvar_todas_posicoes(self):
        from kivy.core.window import Window
        caminho = resource_path_full('posicoes_botoes_inicial.json', 'configs')
        data = {}
        for child in self.ids.values():
            if hasattr(child, 'pos'):
                x_real = (child.pos[0]) * largura_original / Window.width
                y_real = (child.pos[1]) * altura_original / Window.height
                data[child.id] = [x_real, y_real]
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        if hasattr(self, 'popup_dev'):
            self.popup_dev.dismiss()

    def mostrar_posicoes_botao(self):
        for nome, widget in self.ids.items():
            if hasattr(widget, 'pos'):
                print(f'{nome}: {widget.pos}')
        if hasattr(self, 'popup_dev'):
            self.popup_dev.dismiss()


    arraste_liberado = True
    tempos_disponiveis = ListProperty([])
    predef_names = ListProperty([])

    logocafe_path = StringProperty(resource_path_full('logocafé.png', 'assets'))

    def abrir_popup_volume(self):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))

        app = App.get_running_app()

        # 🎵 Música de fundo
        volume_musica = app.musica_fundo.volume if hasattr(app, 'musica_fundo') and app.musica_fundo else 0.5
        slider_musica = Slider(min=0, max=1, value=volume_musica, step=0.01)
        label_musica = Label(text=f"Música: {slider_musica.value:.2f}", font_size=dp(18))

        def on_slider_musica_change(instance, value):
            if hasattr(app, 'musica_fundo') and app.musica_fundo:
                app.musica_fundo.volume = value
            label_musica.text = f"Música: {value:.2f}"

        slider_musica.bind(value=on_slider_musica_change)

        # 🔊 Efeitos sonoros (acerto e erro)
        volume_efeitos = (
            app.som_acerto.volume if hasattr(app, 'som_acerto') and app.som_acerto else 0.5
        )
        slider_efeitos = Slider(min=0, max=1, value=volume_efeitos, step=0.01)
        label_efeitos = Label(text=f"Efeitos: {slider_efeitos.value:.2f}", font_size=dp(18))

        def on_slider_efeitos_change(instance, value):
            if hasattr(app, 'som_acerto') and app.som_acerto:
                app.som_acerto.volume = value
            if hasattr(app, 'som_erro') and app.som_erro:
                app.som_erro.volume = value
            label_efeitos.text = f"Efeitos: {value:.2f}"

        slider_efeitos.bind(value=on_slider_efeitos_change)

        # Montar conteúdo do popup
        content.add_widget(label_musica)
        content.add_widget(slider_musica)
        content.add_widget(label_efeitos)
        content.add_widget(slider_efeitos)

        popup = Popup(
            title='Volume',
            content=content,
            size_hint=(None, None),
            size=(dp(400), dp(300)),
            background = resource_path_full('popup genérico HD.png', 'assets'),
            separator_height=0
        )
        popup.open()

    def configurar_testes_resolucao(self):
        def teclado(window, key, scancode, codepoint, modifiers):
            if key == 282:  # F1
                Window.unbind(on_resize=enforce_size)
                Window.size = (1024, 600)
            elif key == 283:  # F2
                Window.unbind(on_resize=enforce_size)
                Window.size = (1280, 720)
            elif key == 284:  # F3
                Window.unbind(on_resize=enforce_size)
                Window.size = (1366, 768)
            elif key == 285:  # F4
                Window.unbind(on_resize=enforce_size)
                Window.size = (1920, 1080)
            elif key == 293:  # F12 para abrir menu visual
                self.abrir_menu_resolucao()

        Window.bind(on_key_down=teclado)


    def abrir_menu_resolucao(self):
        content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))

        resolucoes = [
            ("1024x600", (1024, 600)),
            ("1280x720", (1280, 720)),
            ("1366x705", (1366, 705)),
            ("1366x768", (1366, 768)),
            ("1920x1080", (1920, 1080))    
        ]

        for texto, tamanho in resolucoes:
            btn = Button(text=texto, size_hint=(1, None), height=dp(40))
            btn.bind(on_release=lambda btn, t=tamanho: self.mudar_resolucao_configuracoes(t))
            # removido: não se usa content aqui
            content.add_widget(btn) 
        popup = Popup(title="Escolher Resolução", content=content,
                      size_hint=(None, None), size=(dp(400), dp(400)))
        popup.open()
        self.popup_resolucao = popup

    
    def mudar_resolucao_configuracoes(self, tamanho):
            global desired_size
            
            print(f"[DEBUG] Mudando resolução para: {tamanho}")
            desired_size = tamanho
            
            # Desliga o 'fiscal' de tamanho temporariamente
            try:
                Window.unbind(on_resize=enforce_size)
            except:
                pass

            # === O TRUQUE PARA TESTES ===
            # Se a largura desejada for maior que a largura da tela real,
            # removemos a borda da janela. O Windows só permite janelas
            # maiores que o monitor se elas não tiverem borda.
            largura_tela_monitor = Window.system_size[0] # Ou use um valor fixo se souber, ex: 1366
            
            if tamanho[0] > 1366: # Se for maior que seu monitor
                Window.borderless = True
                Window.position = 'custom'
                Window.left = 0
                Window.top = 0
            else:
                Window.borderless = False
                Window.position = 'auto'

            # Aplica o tamanho
            Window.size = tamanho
            
            # Re-vincula o 'fiscal' de tamanho
            Window.bind(on_resize=enforce_size)

            # Atualiza layouts internos
            Clock.schedule_once(lambda dt: self.atualizar_layout_resize(), 0.1)
            Clock.schedule_once(lambda dt: self.load_button_positions(), 0.2)

            if hasattr(self, 'popup_resolucao'):
                self.popup_resolucao.dismiss()

    def on_musica_volume_change(instance, value):
            if App.get_running_app().musica_fundo:
                App.get_running_app().musica_fundo.volume = value
            label_musica.text = f"Música de Fundo: {value:.2f}" # type: ignore # type: ignore

            slider_musica.bind(value=on_musica_volume_change) # type: ignore # type: ignore

        # Slider para efeitos sonoros
            slider_efeitos = Slider(
            min=0, max=1, value=App.get_running_app().som_acerto.volume if App.get_running_app().som_acerto else 0.5,
            step=0.01
        )
            label_efeitos = Label(text=f"Efeitos Sonoros: {slider_efeitos.value:.2f}", font_size=dp(20))

    def on_efeitos_volume_change(instance, value):
        if App.get_running_app().som_acerto:
            App.get_running_app().som_acerto.volume = value
            if App.get_running_app().som_erro:
                App.get_running_app().som_erro.volume = value
            label_efeitos.text = f"Efeitos Sonoros: {value:.2f}" # type: ignore

        slider_efeitos.bind(value=on_efeitos_volume_change) # type: ignore

        content.add_widget(label_musica) # type: ignore
        content.add_widget(slider_musica) # type: ignore
        content.add_widget(label_efeitos) # type: ignore
        content.add_widget(slider_efeitos) # type: ignore

        popup = Popup(
            title='Ajustar Volume',
            separator_height=0,
            title_size= dp(20),
            content=content, # type: ignore
            size_hint=(None, None),
            size=(dp(400), dp(300)),
            background = resource_path_full('popup genérico HD.png', 'assets')
        )
        popup.open()

    
    def get_button_pos(self, btn_id, default_x, default_y):
        path = resource_path_full('posicoes_botoes_inicial.json', 'configs')
        data = load_json_cached(path, default={}) or {}
        if btn_id in data:
            return ajustar_posicao_letterbox(data[btn_id])
        
        # Novo cálculo para posição padrão com letterbox
        largura_viewport, altura_viewport, offset_x, offset_y = calcular_viewport()
        return [offset_x + default_x * largura_viewport, offset_y + default_y * altura_viewport]

    def on_pre_enter(self):
        if hasattr(self, 'configurar_modo_dev'):
            self.configurar_modo_dev()

        if hasattr(self, 'configurar_testes_resolucao'):
            self.configurar_testes_resolucao()
        self.tempos_disponiveis = [
            '1:00', '1:30', '2:00', '2:30',
            '3:00', '3:30', '4:00', '4:30',
            '5:00'
        ]
        print(f"[DEBUG] Resolução atual da janela: {Window.width}x{Window.height}")
        Clock.schedule_once(lambda dt: self.load_button_positions(), 0.5)
        self.carregar_predefinicoes()

    def load_button_positions(self):
        path = resource_path_full('posicoes_botoes_inicial.json', 'configs')
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
            print(f"[DEBUG] Resolução atual da janela: {Window.width}x{Window.height}")
            for btn_id, pos in data.items():
                if btn_id in self.ids:
                    novo_pos = ajustar_posicao_letterbox(pos)
                    self.ids[btn_id].pos = novo_pos

    def salvar_posicao_botao(self, btn_id, pos):
        largura_viewport, altura_viewport, offset_x, offset_y = calcular_viewport()
        x_real = (pos[0] - offset_x) * (largura_original / largura_viewport)
        y_real = (pos[1] - offset_y) * (altura_original / altura_viewport)
        path = resource_path_full('posicoes_botoes_inicial.json', 'configs')
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
        data[btn_id] = [x_real, y_real]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    
    def salvar_todas_posicoes(self):
        botoes = ['btn_iniciar', 'btn_adicionar', 'btn_listar', 'btn_voltar',
                  'spinner_game_mode', 'spinner_equipes', 'spinner_tempo', 'spinner_predefinicao', 'btn_volume', 'btn_predefinicoes']
        data = {}
        largura_viewport, altura_viewport, offset_x, offset_y = calcular_viewport()
        for btn_id in botoes:
            if btn_id in self.ids:
                pos = self.ids[btn_id].pos
                x_real = (pos[0] - offset_x) * (largura_original / largura_viewport)
                y_real = (pos[1] - offset_y) * (altura_original / altura_viewport)
                data[btn_id] = [x_real, y_real]
        self.arraste_liberado = False
        path = resource_path_full('posicoes_botoes_inicial.json', 'configs')
        with open(path, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def popup_configurar_predefinicao(self, nome_predefinicao):
        if nome_predefinicao == "Escolher Predefinição":
            return

        path = resource_path_full('predefinicoes.json', 'configs')
        if not os.path.exists(path):
            show_message_popup("Erro", "Arquivo de predefinições não encontrado.")
            return

        with open(path, 'r', encoding='utf-8') as f:
            predefinicoes = json.load(f)

        if nome_predefinicao not in predefinicoes:
            show_message_popup("Erro", "Predefinição não encontrada.")
            return

        predef_data = predefinicoes[nome_predefinicao]

        layout = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))

        tempo_spinner = Spinner(
            text='1:00',
            values=self.tempos_disponiveis,
            background_normal=resource_path_full('botao generico popup generico.png', 'assets'),
            background_down=resource_path_full('botao generico popup generico.png', 'assets'),
            font_size=dp(20),
            size_hint=(1, None),
            height=dp(50)
        )

        equipes_spinner = Spinner(
            text='2',
            values=['2','3','4','5','6','7','8'],
            background_normal=resource_path_full('botao generico popup generico.png', 'assets'),
            background_down=resource_path_full('botao generico popup generico.png', 'assets'),
            font_size=dp(20),
            size_hint=(1, None),
            height=dp(50)
        )

        btn_confirmar = Button(
            text="Iniciar Jogo",
            background_normal=resource_path_full('botao generico popup generico.png', 'assets'),
            background_down=resource_path_full('botao generico popup generico.png', 'assets'),
            font_size=dp(20),
            size_hint=(1, None),
            height=dp(50)
        )

        layout.add_widget(Label(text="Selecione o tempo:", font_size=dp(18)))
        layout.add_widget(tempo_spinner)
        layout.add_widget(Label(text="Selecione o número de equipes:", font_size=dp(18)))
        layout.add_widget(equipes_spinner)
        layout.add_widget(btn_confirmar)

        popup = Popup(
            title='',
            content=layout,
            size_hint=(None, None),
            size=(dp(400), dp(400)),
            separator_height=0,
            background = resource_path_full('popup genérico HD.png', 'assets'),
            background_color=(1,1,1,1)
        )

        def iniciar_com_predefinicao(instance):
            popup.dismiss()

            tela_jogo = self.manager.get_screen('tela_jogo')
            tela_jogo.num_teams = int(equipes_spinner.text)
            tempo_str = tempo_spinner.text
            minutos, segundos = tempo_str.split(':')
            tela_jogo.time_limit = int(minutos) * 60 + int(segundos)

            perguntas = predef_data.get('perguntas', [])
            areas = list(set(p['area'] for p in perguntas))
            dificuldades = list(set(p['dificuldade'].lower() for p in perguntas))

            tela_jogo.selected_areas = areas
            tela_jogo.selected_dificuldades = dificuldades
            try:
                if getattr(tela_jogo, 'session_id', ''):
                    from historico import HistoryManager
                    HistoryManager.set_filters(tela_jogo.session_id, areas, dificuldades)
            except Exception as e:
                print('[HIST] set_filters (predef) erro:', e)

            tela_jogo.usando_predefinicao = True
            tela_jogo.perguntas_predefinicao = perguntas
            tela_jogo.game_mode = predef_data.get('modo', 'Coffee Lovers')
            tela_jogo.jogo_iniciado = False

            app = App.get_running_app()
            if getattr(app, 'game_started_once', False):
                self.abrir_com_preload('tela_jogo') if hasattr(self, 'abrir_com_preload') else setattr(self.manager, 'current', 'loading_screen')
            else:
                app.game_started_once = True
                self.manager.current = 'video_screen'

        btn_confirmar.bind(on_release=iniciar_com_predefinicao)
        popup.open()

    def carregar_predefinicoes(self):
        path = resource_path_full('predefinicoes.json', 'configs')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                predefinicoes = json.load(f)
                self.predef_names = list(predefinicoes.keys())
        else:
            self.predef_names = []

    def iniciar_com_predefinicao(instance):
        popup.dismiss() # type: ignore

        tela_jogo = self.manager.get_screen('tela_jogo') # type: ignore
        tela_jogo.num_teams = int(equipes_spinner.text) # type: ignore
        tempo_str = tempo_spinner.text # type: ignore
        minutos, segundos = tempo_str.split(':')
        tela_jogo.time_limit = int(minutos) * 60 + int(segundos)

        perguntas = predef_data.get('perguntas', []) # type: ignore
        areas = list(set(p['area'] for p in perguntas))
        dificuldades = list(set(p['dificuldade'].lower() for p in perguntas))

        tela_jogo.selected_areas = areas
        tela_jogo.selected_dificuldades = dificuldades
        tela_jogo.usando_predefinicao = True
        tela_jogo.perguntas_predefinicao = perguntas
        tela_jogo.game_mode = predef_data.get('modo', 'Coffee Lovers') # type: ignore
        tela_jogo.jogo_iniciado = False

        app = App.get_running_app()
        if getattr(app, 'game_started_once', False):
            self.abrir_com_preload('tela_jogo') if hasattr(self, 'abrir_com_preload') else setattr(self.manager, 'current', 'loading_screen')
        else:
            app.game_started_once = True
            self.manager.current = 'video_screen' # type: ignore

        btn_confirmar.bind(on_release=iniciar_com_predefinicao) # type: ignore
        popup.open() # type: ignore

    def show_message_popup(title, message):
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=[dp(30), dp(30), dp(30), dp(30)]
        )

        # Mensagem com alinhamento central e cor branca
        label = Label(
            text=message,
            font_size=dp(20),
            halign='center',
            valign='middle',
            color=(1, 1, 1, 1)
        )
        label.bind(size=label.setter('text_size'))

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

        # Criação do popup com fundo personalizado e sem título
        popup = Popup(
            title='',
            separator_height=0,
            title_size=0,
            content=content,
            size_hint=(None, None),
            size=(dp(500), dp(250)),
            background=resource_path_full('popup genérico HD.png', 'assets'),
            background_color=(1, 1, 1, 1)
        )

        ok_button.bind(on_press=lambda *args: popup.dismiss())
        popup.open()

    def iniciar_jogo(self):
        try:
            game_mode = self.ids.spinner_game_mode.text
            num_teams = int(self.ids.spinner_equipes.text)
            tempo_str = self.ids.spinner_tempo.text
            mm, ss = tempo_str.split(':')
            total_segundos = int(mm) * 60 + int(ss)
            sid = HistoryManager.start_session(game_mode, num_teams, total_segundos, metadata={'modo': game_mode})
            tela_jogo = self.manager.get_screen('tela_jogo')
            tela_jogo.session_id = sid
            tela_jogo.game_mode = game_mode
        except Exception as _e:
            print('[HIST] erro:', _e)

        if self.ids.spinner_game_mode.text == "Clique para escolher":
            # Corrigido: usa a função global show_message_popup
            show_message_popup("Erro", "Por favor, escolha um modo de jogo!")
            return

        tela_jogo = self.manager.get_screen('tela_jogo')
        tela_jogo.num_teams = int(self.ids.spinner_equipes.text)
        tempo_str = self.ids.spinner_tempo.text
        minutos, segundos = tempo_str.split(':')
        total_segundos = int(minutos) * 60 + int(segundos)
        tela_jogo.time_limit = total_segundos
        modo_jogo = self.ids.spinner_game_mode.text

        tela_jogo.game_mode = modo_jogo
        self.manager.get_screen('add_edit_question').game_mode = modo_jogo
        self.manager.get_screen('question_list').game_mode = modo_jogo
        db_file = get_db_filename(modo_jogo)

        try:
            data = load_json_cached(db_file, default={})
            areas = list(data.get('areas', {}).keys())
            dificuldades = data.get('dificuldades', [])
        except FileNotFoundError:
            show_message_popup("Erro", "Arquivo de perguntas não encontrado.")
            return
        except json.JSONDecodeError as e:
            show_message_popup("Erro", "Erro ao ler o arquivo de perguntas.")
            return

        # Layout principal do popup
        popup_layout = BoxLayout(
            orientation='vertical',
            padding=[dp(20), dp(5), dp(20), dp(60)],
            spacing=dp(15),
            size_hint_y=None
        )
        popup_layout.bind(minimum_height=popup_layout.setter('height'))

        # Título
        titulo = Label(
            text="Selecione as Áreas e Dificuldades",
            font_size=dp(22),
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(40),  # ou dp(30) se preferir menor
            halign='center',
            valign='middle'
        )
        titulo.bind(size=titulo.setter('text_size'))
        popup_layout.add_widget(titulo)

        # Layout de Áreas
        areas_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        areas_layout.bind(minimum_height=areas_layout.setter('height'))
        for area in reversed(areas):
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
            checkbox = CheckBox(active=True)
            label = Label(text=area, halign='left', valign='middle', font_size=dp(20))
            label.bind(size=label.setter('text_size'))
            box.add_widget(checkbox)
            box.add_widget(label)
            areas_layout.add_widget(box)
        areas_scroll = ScrollView(size_hint=(1, 1))
        areas_scroll.add_widget(areas_layout)

        # Layout de Dificuldades
        dificuldades_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        dificuldades_layout.bind(minimum_height=dificuldades_layout.setter('height'))
        for dificuldade in reversed(dificuldades):
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
            checkbox = CheckBox(active=True)
            label = Label(text=dificuldade, halign='left', valign='middle', font_size=dp(20))
            label.bind(size=label.setter('text_size'))
            box.add_widget(checkbox)
            box.add_widget(label)
            dificuldades_layout.add_widget(box)
        dificuldades_scroll = ScrollView(size_hint=(1, 1))
        dificuldades_scroll.add_widget(dificuldades_layout)

        # Novo layout horizontal para Áreas e Dificuldades lado a lado
        areas_dificuldades_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(20),
            size_hint_y=None,
            height=dp(300)  # Você pode ajustar essa altura se quiser
        )

        # Box individual para Áreas
        area_box = BoxLayout(orientation='vertical', size_hint=(0.5, 1))
        area_box.add_widget(Label(text="Áreas:", size_hint_y=None, height=dp(30), font_size=dp(20)))
        area_box.add_widget(areas_scroll)

        # Box individual para Dificuldades
        dificuldade_box = BoxLayout(orientation='vertical', size_hint=(0.5, 1))
        dificuldade_box.add_widget(Label(text="Dificuldades:", size_hint_y=None, height=dp(30), font_size=dp(20)))
        dificuldade_box.add_widget(dificuldades_scroll)

        # Adicionar ambos no layout principal horizontal
        areas_dificuldades_layout.add_widget(area_box)
        areas_dificuldades_layout.add_widget(dificuldade_box)

        # Adicionar o layout horizontal ao layout principal
        popup_layout.add_widget(areas_dificuldades_layout)

        # Botões de Confirmar e Cancelar
        buttons_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10),
            padding=[dp(80), dp(5), dp(80), dp(0)]  # [left, top, right, bottom]

        )

        confirmar_btn = Button(
            text="Iniciar",
            font_size=dp(22),   # <<< Aqui muda o tamanho da fonte
            width=dp(190),     # <<< Aqui você define a largura que quiser
            background_normal=resource_path_full('botao generico popup generico.png', 'assets'),
            background_down=resource_path_full('botao generico popup generico.png', 'assets'),
            color=(1, 1, 1, 1)
        )

        cancelar_btn = Button(
            text="Cancelar",
            font_size=dp(20),   # <<< Aqui muda o tamanho da fonte
            width=dp(200),     # <<< Aqui você define a largura que quiser
            background_normal=resource_path_full('botao generico popup generico.png', 'assets'),
            background_down=resource_path_full('botao generico popup generico.png', 'assets'),
            color=(1, 1, 1, 1)
        )

        buttons_layout.add_widget(confirmar_btn)
        buttons_layout.add_widget(cancelar_btn)
        popup_layout.add_widget(buttons_layout)

        # Criação do popup final
        popup = Popup(
            title='',
            title_size=0,
            separator_height=0,
            content=popup_layout,
            size_hint=(0.8, 0.8),
            background = resource_path_full('popup generico 2.png', 'assets'),
            background_color=(1, 1, 1, 1)
)

        def iniciar_jogo_confirmado(instance):
            selected_areas = []
            for child in areas_layout.children:
                checkbox = None
                label = None
                for widget in child.children:
                    if isinstance(widget, CheckBox):
                        checkbox = widget
                    elif isinstance(widget, Label):
                        label = widget
                if checkbox and checkbox.active:
                    selected_areas.append(label.text)
            selected_areas = list(reversed(selected_areas))
            selected_dificuldades = []
            for child in dificuldades_layout.children:
                checkbox = None
                label = None
                for widget in child.children:
                    if isinstance(widget, CheckBox):
                        checkbox = widget
                    elif isinstance(widget, Label):
                        label = widget
                if checkbox and checkbox.active:
                    selected_dificuldades.append(label.text.lower())
            if not selected_areas:
                popup.dismiss()
                show_message_popup("Erro", "Selecione pelo menos uma área.")
                return
            if not selected_dificuldades:
                popup.dismiss()
                show_message_popup("Erro", "Selecione pelo menos uma dificuldade.")
                return
            tela_jogo.selected_areas = selected_areas
            tela_jogo.selected_dificuldades = selected_dificuldades
            popup.dismiss()
            # grava no histórico as áreas e dificuldades escolhidas
            try:
                if getattr(tela_jogo, 'session_id', ''):
                    from historico import HistoryManager
                    HistoryManager.set_filters(tela_jogo.session_id, selected_areas, selected_dificuldades)
            except Exception as e:
                print('[HIST] set_filters erro:', e)

            app = App.get_running_app()
            if getattr(app, 'game_started_once', False):
                self.abrir_com_preload('tela_jogo') if hasattr(self, 'abrir_com_preload') else setattr(self.manager, 'current', 'loading_screen')
            else:
                app.game_started_once = True
                self.manager.current = 'video_screen'

        def cancelar_jogo(instance):
            popup.dismiss()
        confirmar_btn.bind(on_press=iniciar_jogo_confirmado)
        cancelar_btn.bind(on_press=cancelar_jogo)
        popup.open()

class TelaJogo(Screen):

    session_id = StringProperty("")
    _q_counter = NumericProperty(0)
    jogo_iniciado = BooleanProperty(False)
    num_teams = NumericProperty(0)
    scores = ListProperty([])
    current_team = NumericProperty(0)
    time_limit = NumericProperty(60)
    selected_areas = ListProperty([])
    selected_dificuldades = ListProperty([])
    game_mode = StringProperty("1º ano")
    usando_predefinicao = BooleanProperty(False)
    perguntas_predefinicao = ListProperty([])  # Armazena perguntas vindas da predefinição
    
    def preparar_jogo_rapido(self):
        """Precarrega placar e roda para evitar tela preta na transição."""
        try:
            if not self.scores or len(self.scores) != self.num_teams:
                self.scores = [0] * max(1, self.num_teams)
                self.current_team = 0
                self.atualizar_scoreboard()
            self.atualizar_roda()
        except Exception as e:
            print(f"[preload] falha ao preparar jogo: {e}")

    
    def on_enter(self):
        if not self.jogo_iniciado:
            self.scores = [0] * self.num_teams
            self.current_team = 0
            self.atualizar_scoreboard()
        self.jogo_iniciado = True
        self.atualizar_roda()

    def on_leave(self):
        self.jogo_iniciado = False
        self.ids.rotating_wheel.stop_animation()
        self.ids.rotating_wheel.unbind(on_area_selected=self.mostrar_pergunta_popup)

    def atualizar_roda(self):
        rotating_wheel = self.ids.rotating_wheel

        if self.usando_predefinicao:
            # Jogando com predefinição
            areas = list(set(p['area'] for p in self.perguntas_predefinicao))
            cores = [[random.random(), random.random(), random.random(), 1] for _ in areas]  # Cor aleatória para cada área
            perguntas_por_area = {area: [p for p in self.perguntas_predefinicao if p['area'] == area] for area in areas}

            rotating_wheel.area_names = areas
            rotating_wheel.segments = len(areas)
            rotating_wheel.colors = cores
            rotating_wheel.update_canvas()

            self.perguntas_por_area = perguntas_por_area

        else:
            # Modo de jogo normal (carregar banco de dados)
            db_file = get_db_filename(self.game_mode)
            areas, cores, perguntas_por_area = self.carregar_dados_json(db_file)
            filtered_areas = [area for area in areas if area in self.selected_areas]
            filtered_cores = [cores[areas.index(area)] for area in filtered_areas]
            rotating_wheel.area_names = filtered_areas
            rotating_wheel.segments = len(filtered_areas)
            rotating_wheel.colors = filtered_cores
            rotating_wheel.update_canvas()

            self.perguntas_por_area = {
                area: [per for per in perguntas_por_area.get(area, []) if per.get('dificuldade', '').lower() in self.selected_dificuldades]
                for area in filtered_areas
            }

        rotating_wheel.unbind(on_area_selected=self.mostrar_pergunta_popup)
        rotating_wheel.bind(on_area_selected=self.mostrar_pergunta_popup)


    def carregar_dados_json(self, db_file):
        try:
            with open(db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                areas = list(data.get('areas', {}).keys())
                cores = list(data.get('areas', {}).values())
                perguntas = data.get('perguntas', [])
                perguntas_por_area = { area: [per for per in perguntas if per['area'] == area] for area in areas }
                return areas, cores, perguntas_por_area
        except (FileNotFoundError, json.JSONDecodeError):
            return [], [], {}

    def girar_roda(self):
        rotating_wheel = self.ids.rotating_wheel
        if rotating_wheel.is_animating:
            return
        initial_speed = random.uniform(800, 900)
        acceleration_duration = 0.1
        deceleration_duration = random.uniform(4, 6)
        rotating_wheel.start_animation(
            initial_speed=initial_speed,
            acceleration_duration=acceleration_duration,
            deceleration_duration=deceleration_duration
        )

    def encerrar_jogo(self):
        try:
            if getattr(self, 'session_id', ''):
                HistoryManager.end_session(self.session_id, final_scoreboard={f"Equipe {i+1}": int(self.scores[i]) for i in range(len(self.scores))})

                self.session_id = ""
        except Exception as _e:
            print('[HIST] erro:', _e)

        if not self.scores:
            return
        max_points = max(self.scores)
        winning_teams = [i + 1 for i, score in enumerate(self.scores) if score == max_points]
        if len(winning_teams) == 1:
            winning_text = f"Equipe {winning_teams[0]} venceu com {max_points} pontos!"
        else:
            teams_str = ', '.join(str(team) for team in winning_teams)
            winning_text = f"Empate entre as equipes: {teams_str} com {max_points} pontos!"

        popup = show_message_popup("Jogo Encerrado", winning_text)
        popup.bind(on_dismiss=lambda inst: self.voltar_para_intro())

    def voltar_para_intro(self):
        self.usando_predefinicao = False
        self.perguntas_predefinicao = []
        self.manager.current = 'intro_screen'


    def mostrar_pergunta_popup(self, instance, area_selecionada):
        area_final = area_selecionada
        if not area_final:
            show_message_popup("Erro", "Nenhuma área foi selecionada!")
            return
        if "pontos" in area_final:
            if "+5 pontos 1" in area_final or "+5 pontos 2" in area_final:
                self.adicionar_pontos(5)
            elif "-5 pontos 1" in area_final or "-5 pontos 2" in area_final:
                self.subtrair_pontos(5)
            return

        pergunta = self.sortear_pergunta(area_final)

        # Índice sequencial para a pergunta desta sessão
        q_idx = int(getattr(self, "_q_counter", 0))
        self._q_counter = q_idx + 1
        if not pergunta:
            rotating_wheel = self.ids.rotating_wheel
            if area_final in rotating_wheel.area_names:
                area_index = rotating_wheel.area_names.index(area_final)
                rotating_wheel.area_names.pop(area_index)
                rotating_wheel.colors.pop(area_index)
                rotating_wheel.segments = len(rotating_wheel.area_names)
                if area_final in self.perguntas_por_area:
                    del self.perguntas_por_area[area_final]
                rotating_wheel.update_canvas()
            return

        # Obter cor associada à área
        cor_area = [0.2, 0.2, 0.2, 1]  # cor padrão
        for seg in self.ids.rotating_wheel.segments_data:
            if seg['nome'] == area_final:
                cor_area = seg['cor']
                break

        time_left = self.time_limit
        initial_time_left = time_left
        _question_started_at = _time.time()
        _question_ctx = {'tipo':'pergunta','equipe': self.current_team+1, 'area': area_final}
        timer_label = Label(
            text=f"Tempo restante: {time_left}s",
            size_hint_y=None,
            height=dp(48),
            color=(1, 1, 1, 1),
            font_size=dp(18)
        )

        def countdown(dt):
            nonlocal time_left
            if time_left <= 0:
                Clock.unschedule(countdown_event)
                popup.dismiss()
                self.pular_vez_por_tempo()
                return
            time_left -= 1
            timer_label.text = f"Tempo restante: {time_left}s"

        countdown_event = Clock.schedule_interval(countdown, 1)

        def stop_countdown(*args):
            Clock.unschedule(countdown_event)


        # Layout raiz do popup de pergunta: timer fixo em cima + conteúdo rolável (pergunta + alternativas)
        root_layout = BoxLayout(orientation='vertical', padding=[dp(40), dp(15), dp(40), dp(25)], spacing=dp(15))

        # Timer fica fixo no topo
        root_layout.add_widget(timer_label)

        # Área rolável para pergunta e alternativas
        scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        scroll_content = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, padding=[dp(40), 0, dp(40), dp(10)])
        scroll_content.bind(minimum_height=scroll_content.setter('height'))

        pergunta_text = pergunta.get('pergunta', 'Pergunta não encontrada.')
        pergunta_label = Label(
            text=f"[Equipe {self.current_team+1}] {pergunta_text}",
            size_hint_y=None,
            font_size=dp(20),
            color=(1, 1, 1, 1),
            halign='center',
            valign='top'
        )

        # Garante quebra de linha dentro do popup e ajusta a altura conforme o texto
        def _update_pergunta_label_size(*args):
            pergunta_label.text_size = (pergunta_label.width, None)
            pergunta_label.texture_update()
            pergunta_label.height = pergunta_label.texture_size[1]

        pergunta_label.bind(width=_update_pergunta_label_size)
        Clock.schedule_once(lambda dt: _update_pergunta_label_size(), 0)

        scroll_content.add_widget(pergunta_label)

        alternativas = pergunta.get('alternativas', []).copy()
        resposta_correta = pergunta.get('correta')
        alternativas.append("Dica")

        def verificar_resposta(instance_btn, alternativa_index):
            if alternativa_index == resposta_correta:
                try:
                    _resp_time = int(self.time_limit - (time_left))
                except Exception:
                    _resp_time = None
                
                try:
                    _resp_time = None
                    try:
                        _resp_time = int(self.time_limit - (time_left))
                    except Exception:
                        _resp_time = None
                    _resp_ms = None if _resp_time is None else int(_resp_time * 1000)
                    _predef_ms = int(self.time_limit * 1000) if hasattr(self, 'time_limit') else None
                    _sid = getattr(self, 'session_id', '')
                    if _sid:
                        HistoryManager.log_question(
                            _sid,
                            q_idx if 'q_idx' in locals() else 0,
                            area=area_final,
                            difficulty=pergunta.get('dificuldade', 'Fácil'),
                            correct=True,
                            chosen_option=alternativa_index if 'alternativa_index' in locals() else None,
                            correct_option=pergunta.get('correta'),
                            response_time_ms=_resp_ms,
                            predefined_time_ms=_predef_ms,
                            question_id=pergunta.get('pergunta', ''),
                            equipe=int(self.current_team) + 1
                        )
                except Exception as _e:
                    print('[HIST] erro ao registrar pergunta:', _e)

                App.get_running_app().som_acerto.play()
                stop_countdown()
                dificuldade = pergunta.get('dificuldade', 'Fácil')
                pontos = self.calcular_pontos(dificuldade)
                self.scores[self.current_team] += pontos
                self.exibir_feedback_pontos(f"+{pontos} pontos adicionados!")
                self.atualizar_scoreboard()
                popup.dismiss()
                self.next_team()
            elif alternativa_index == len(alternativas) - 1:
                dica_texto = pergunta.get('dica_texto', '')
                dica_imagem = pergunta.get('dica_imagem', '')
                mostrar_dica(self, dica_texto, resource_path_full(dica_imagem) if dica_imagem else None)

            else:
                App.get_running_app().som_erro.play()
                try:
                    _resp_time = int(self.time_limit - (time_left))
                except Exception:
                    _resp_time = None
                
                try:
                    _resp_time = None
                    try:
                        _resp_time = int(self.time_limit - (time_left))
                    except Exception:
                        _resp_time = None
                    _resp_ms = None if _resp_time is None else int(_resp_time * 1000)
                    _predef_ms = int(self.time_limit * 1000) if hasattr(self, 'time_limit') else None
                    _sid = getattr(self, 'session_id', '')
                    if _sid:
                        HistoryManager.log_question(
                            _sid,
                            q_idx if 'q_idx' in locals() else 0,
                            area=area_final,
                            difficulty=pergunta.get('dificuldade', 'Fácil'),
                            correct=False,
                            chosen_option=alternativa_index if 'alternativa_index' in locals() else None,
                            correct_option=pergunta.get('correta'),
                            response_time_ms=_resp_ms,
                            predefined_time_ms=_predef_ms,
                            question_id=pergunta.get('pergunta', ''),
                            equipe=int(self.current_team) + 1
                        )
                except Exception as _e:
                    print('[HIST] erro ao registrar pergunta:', _e)

                stop_countdown()
                self.exibir_feedback_pontos("Que pena, você errou!")
                popup.dismiss()
                self.next_team()


        for i, alt in enumerate(alternativas):
            btn = Button(
                text=alt,
                size_hint_y=None,
                height=dp(48),
                background_normal=resource_path_full('botao generico popup generico.png', 'assets'),
                background_down=resource_path_full('botao generico popup generico.png', 'assets'),
                color=(1, 1, 1, 1),
                font_size=dp(18)
            )
            btn.bind(on_press=lambda btn_inst, idx=i: verificar_resposta(btn_inst, idx))
            scroll_content.add_widget(btn)

        scroll_view.add_widget(scroll_content)
        root_layout.add_widget(scroll_view)

        popup = Popup(
            title='',
            separator_height=0,
            title_size=0,
            content=root_layout,
            size_hint=(0.8, 0.7),
            background = resource_path_full('popup genérico HD.png', 'assets'),
            background_color=cor_area[:3] + [0.3],
            overlay_color=(0, 0, 0, 0.9)
        )

        popup.open()

    def pular_vez_por_tempo(self):
        # [REVIEW] Conversão manual necessária: _hist_log({'tipo':'tempo_esgotado', 'equipe': self.current_team+1, 'tempo_predefinido': getattr(self, 'time_limit', None)})
        show_message_popup("Tempo Esgotado", "Infelizmente o tempo se esgotou!")
        self.next_team()

    def sortear_pergunta(self, area):
        perguntas_da_area = self.perguntas_por_area.get(area, [])
        perguntas_validas = [
            p for p in perguntas_da_area
            if isinstance(p.get('alternativas'), list)
            and len(p['alternativas']) == 4
            and p.get('correta') is not None
        ]
        if perguntas_validas:
            pergunta_selecionada = random.choice(perguntas_validas)
            return pergunta_selecionada
        return None

    def calcular_pontos(self, dificuldade_str):
        diff_map = {
            '1': 15,
            '2': 20,
            '3': 30,
            'fácil': 15,
            'médio': 20,
            'difícil': 30
        }
        pontos = diff_map.get(dificuldade_str.lower(), 15)
        return pontos

    def atualizar_scoreboard(self):
        layout = self.ids.scoreboard_layout
        layout.clear_widgets()
        for i, score in enumerate(self.scores):
            layout.add_widget(Label(text=f"Equipe {i+1}: {score}"))

    def adicionar_pontos(self, pontos):
        self.scores[self.current_team] += pontos
        self.atualizar_scoreboard()
        self.exibir_feedback_pontos(f"+{pontos} pontos adicionados!")

    def subtrair_pontos(self, pontos):
        self.scores[self.current_team] -= pontos
        if self.scores[self.current_team] < 0:
            self.scores[self.current_team] = 0
        self.atualizar_scoreboard()
        self.exibir_feedback_pontos(f"-{pontos} pontos subtraídos!")

    def exibir_feedback_pontos(self, mensagem):
        show_message_popup("Pontos", mensagem)

    def next_team(self):
        self.current_team = (self.current_team + 1) % self.num_teams

class AddEditQuestionScreen(Screen):
    available_areas = ListProperty([])
    cor_selecionada = ListProperty([1, 1, 1, 1])
    game_mode = StringProperty("Coffee Lovers")

    def on_pre_enter(self):
        if hasattr(self, 'configurar_modo_dev'):
            self.configurar_modo_dev()

        if hasattr(self, 'configurar_testes_resolucao'):
            self.configurar_testes_resolucao()
        self.tempos_disponiveis = [
            '1:00', '1:30', '2:00', '2:30',
            '3:00', '3:30', '4:00', '4:30',
            '5:00'
        ]
        self.game_mode = self.manager.get_screen('tela_jogo').game_mode
        self.carregar_areas_existentes()
        
        carregar_posicoes(self, resource_path_full('posicoes_botoes_fake.json', 'configs'))

    def carregar_areas_existentes(self):
        db_file = get_db_filename(self.game_mode)
        try:
            with open(db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                areas = list(data.get('areas', {}).keys())
                self.available_areas = areas
                self.ids.area_spinner.values = self.available_areas
        except FileNotFoundError:
            self.available_areas = []
            self.ids.area_spinner.values = []
            show_message_popup("Erro", "Arquivo de perguntas não encontrado.")

    def selecionar_area(self, area):
        cor = self.obter_cor_area(area)
        if cor:
            self.atualizar_cor_selecionada(cor)

    def obter_cor_area(self, area):
        db_file = get_db_filename(self.game_mode)
        try:
            with open(db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                areas = data.get('areas', {})
                cor = areas.get(area, [1, 1, 1, 1])
                return cor
        except FileNotFoundError:
            return [1, 1, 1, 1]

    def adicionar_area(self):
        nova_area = self.ids.nova_area.text.strip()
        if nova_area and nova_area not in self.available_areas:
            content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
            color_picker = ColorPicker()

            select_button = Button(
                text='Selecionar Cor',
                size_hint_y=None,
                height=dp(48),
                font_size=dp(20),
                color=(1, 1, 1, 1),
                background_normal=resource_path_full('botao generico popup generico.png', 'assets'),
                background_down=resource_path_full('botao generico popup generico.png', 'assets'),
            )

            content.add_widget(color_picker)
            content.add_widget(select_button)

            popup = Popup(
                title='Selecione uma Cor para a Nova Área',
                background=resource_path_full('popup genérico HD.png', 'assets'),
                content=content,
                size_hint=(0.8, 0.8),
                separator_height=0,   # aqui sim é válido
            )

            def on_select(instance):
                cor = color_picker.color
                self.cor_selecionada = cor
                self.atualizar_botao_cor(cor)
                self.salvar_nova_area(nova_area, cor)
                popup.dismiss()

            select_button.bind(on_press=on_select)
            popup.open()
        else:
            show_message_popup("Erro", "Área inválida ou já existente.")


    def salvar_nova_area(self, area, cor):
        db_file = get_db_filename(self.game_mode)
        try:
            with open(db_file, 'r+', encoding='utf-8') as f:
                data = json.load(f)
                data.setdefault('areas', {})[area] = cor
                f.seek(0)
                json.dump(data, f, ensure_ascii=False, indent=4)
                f.truncate()
            self.available_areas.append(area)
            self.ids.area_spinner.values = self.available_areas
            self.ids.area_spinner.text = area
            self.ids.nova_area.text = ''
        except FileNotFoundError:
            show_message_popup("Erro", "Arquivo de perguntas não encontrado.")

    def mostrar_seletor_cor(self):
        if self.ids.area_spinner.text == 'Selecione uma Área':
            show_message_popup("Selecione uma Área Primeiro", "Por favor, selecione uma área para definir sua cor.")
            return

        # Layout interno do popup com padding e spacing
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(5),          # espaço entre o colorpicker e o botão
            padding=dp(40)           # espaço dentro das bordas
        )

        # ColorPicker
        color_picker = ColorPicker()

        # Botão estilizado com imagem de fundo e texto branco
        select_button = Button(
            text='Selecionar Cor',
            size_hint_y=None,
            height=dp(48),
            font_size=dp(20),
            color=(1, 1, 1, 1),
            background_normal=resource_path_full('botao generico popup generico.png', 'assets'),
            background_down=resource_path_full('botao generico popup generico.png', 'assets'))

        # Adiciona os elementos ao layout
        content.add_widget(color_picker)
        content.add_widget(select_button)

        # Cria o popup com imagem de fundo transparente
        popup = Popup(
            title='Selecione uma Nova Cor para a Área',
            title_size=dp(20),
            separator_height=0,
            background = resource_path_full('popup genérico HD.png', 'assets'),
            background_color=(1, 1, 1, 1),
            content=content,
            size_hint=(0.8, 0.8)  # ou ajuste como preferir
        )

        # Ação ao clicar no botão
        def on_select(instance):
            cor = color_picker.color
            self.cor_selecionada = cor
            self.atualizar_botao_cor(cor)
            self.salvar_cor_area(self.ids.area_spinner.text, cor)
            popup.dismiss()

        select_button.bind(on_press=on_select)

        # Abre o popup
        popup.open()

        def on_select(instance):
            cor = color_picker.color
            self.cor_selecionada = cor
            self.atualizar_botao_cor(cor)
            self.salvar_cor_area(self.ids.area_spinner.text, cor)
            popup.dismiss()
        select_button.bind(on_press=on_select)
        popup.open()

    def salvar_cor_area(self, area, cor):
        db_file = get_db_filename(self.game_mode)
        try:
            with open(db_file, 'r+', encoding='utf-8') as f:
                data = json.load(f)
                data.setdefault('areas', {})[area] = cor
                f.seek(0)
                json.dump(data, f, ensure_ascii=False, indent=4)
                f.truncate()
            self.atualizar_botao_cor(cor)
        except FileNotFoundError:
            show_message_popup("Erro", "Arquivo de perguntas não encontrado.")

    def atualizar_cor_selecionada(self, cor):
        self.cor_selecionada = cor
        self.atualizar_botao_cor(cor)

    def atualizar_botao_cor(self, cor):
        self.ids.escolher_cor.background_color = cor

    def salvar_pergunta(self):
        area = self.ids.area_spinner.text.strip()
        question = self.ids.pergunta.text.strip()
        alternativa1 = self.ids.alternativa1.text.strip()
        alternativa2 = self.ids.alternativa2.text.strip()
        alternativa3 = self.ids.alternativa3.text.strip()
        alternativa4 = self.ids.alternativa4.text.strip()
        resposta_correta = self.ids.resposta_correta.text.strip()
        dificuldade = self.ids.dificuldade.text.strip()
        dica_texto = self.ids.dica_texto.text.strip()
        dica_imagem = self.ids.dica_imagem.text.strip()
        if not all([area, question, alternativa1, alternativa2, alternativa3, alternativa4, resposta_correta, dificuldade]):
            show_message_popup("Erro", "Todos os campos obrigatórios devem ser preenchidos.")
            return
        try:
            resposta_correta = int(resposta_correta)
            if resposta_correta < 0 or resposta_correta > 3:
                raise ValueError
        except ValueError:
            show_message_popup("Erro", "Resposta correta deve ser um número entre 0 e 3.")
            return
        db_file = get_db_filename(self.game_mode)
        try:
            with open(db_file, 'r+', encoding='utf-8') as f:
                data = json.load(f)
                perguntas = data.get('perguntas', [])
                areas = data.get('areas', {})
                if area not in areas:
                    areas[area] = self.cor_selecionada
                nova_pergunta = {
                    'area': area,
                    'pergunta': question,
                    'alternativas': [
                        alternativa1,
                        alternativa2,
                        alternativa3,
                        alternativa4
                    ],
                    'correta': resposta_correta,
                    'dificuldade': dificuldade.lower(),
                    'dica_texto': dica_texto,
                    'dica_imagem': dica_imagem
                }
                if hasattr(self, 'editing_index') and self.editing_index is not None:
                    perguntas[self.editing_index] = nova_pergunta
                else:
                    perguntas.append(nova_pergunta)
                data['perguntas'] = perguntas
                data['areas'] = areas
                f.seek(0)
                json.dump(data, f, ensure_ascii=False, indent=4)
                f.truncate()
        except FileNotFoundError:
            show_message_popup("Erro", "Arquivo de perguntas não encontrado.")
            return
        self.reset_fields()
        self.manager.current = 'tela_inicial'

    def load_question_for_editing(self, question_index):
        db_file = get_db_filename(self.game_mode)
        try:
            with open(db_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                questions = data.get('perguntas', [])
                areas = data.get('areas', {})
                if question_index >= len(questions):
                    raise IndexError("Índice da pergunta fora do intervalo.")
                question = questions[question_index]
                self.editing_index = question_index
                self.ids.area_spinner.text = question['area']
                self.ids.pergunta.text = question['pergunta']
                self.ids.alternativa1.text = question['alternativas'][0]
                self.ids.alternativa2.text = question['alternativas'][1]
                self.ids.alternativa3.text = question['alternativas'][2]
                self.ids.alternativa4.text = question['alternativas'][3]
                self.ids.resposta_correta.text = str(question['correta'])
                self.ids.dificuldade.text = question['dificuldade'].capitalize()
                self.ids.dica_texto.text = question.get('dica_texto', '')
                self.ids.dica_imagem.text = question.get('dica_imagem', '')
                cor = areas.get(question['area'], [1, 1, 1, 1])
                self.atualizar_cor_selecionada(cor)
        except (IndexError, FileNotFoundError):
            show_message_popup("Erro", "Erro ao carregar a pergunta para edição.")

    def reset_fields(self):
        self.ids.area_spinner.text = 'Selecione uma Área'
        self.ids.nova_area.text = ''
        self.ids.pergunta.text = ''
        self.ids.alternativa1.text = ''
        self.ids.alternativa2.text = ''
        self.ids.alternativa3.text = ''
        self.ids.alternativa4.text = ''
        self.ids.resposta_correta.text = ''
        self.ids.dificuldade.text = 'Fácil'
        self.ids.dica_texto.text = ''
        self.ids.dica_imagem.text = ''
        self.atualizar_botao_cor([1, 1, 1, 1])
        self.editing_index = None

    def cancelar_pergunta(self):
        self.reset_fields()
        self.manager.current = 'tela_inicial'

    def abrir_filechooser(self):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        filechooser = FileChooserListView(filters=['*.png', '*.jpg', '*.jpeg', '*.gif'], size_hint=(1, 0.9))
        buttons = BoxLayout(size_hint=(1, 0.1), spacing=dp(10))
        selecionar_btn = Button(text='Selecionar')
        cancelar_btn = Button(text='Cancelar')
        buttons.add_widget(selecionar_btn)
        buttons.add_widget(cancelar_btn)
        content.add_widget(filechooser)
        content.add_widget(buttons)
        popup = Popup(
            title='Selecionar Imagem',
            content=content,
            size_hint=(0.9, 0.9)
        )
        def selecionar(instance):
            if filechooser.selection:
                selected_path = filechooser.selection[0]
                self.ids.dica_imagem.text = selected_path
                popup.dismiss()
        def cancelar(instance):
            popup.dismiss()
        selecionar_btn.bind(on_press=selecionar)
        cancelar_btn.bind(on_press=cancelar)
        popup.open()

class QuestionListScreen(Screen):
    _pending_items = None
    _build_ev = None

    arraste_liberado = True
    game_mode = StringProperty("Coffee Lovers")
    available_areas = ListProperty([])
    available_difficulties = ListProperty(['Fácil', 'Médio', 'Difícil'])  # <- ISSO RESOLVE O ERRO DO SPINNER

    def get_button_pos(self, btn_id, default_x, default_y):
        return self.button_positions.get(btn_id, (Window.width * default_x, Window.height * default_y))

    def on_pre_enter(self):
        print("[DEBUG] Entrou na QuestionListScreen")
        carregar_posicoes(self, resource_path_full("posicoes_botoes_listar.json", "configs"))
        self.carregar_areas()
        self.carregar_perguntas()

        self.carregar_areas()
        self.carregar_perguntas()
        if hasattr(self, 'configurar_modo_dev'):
            self.configurar_modo_dev()

        if hasattr(self, 'configurar_testes_resolucao'):
            self.configurar_testes_resolucao()
        self.tempos_disponiveis = [
            '1:00', '1:30', '2:00', '2:30',
            '3:00', '3:30', '4:00', '4:30',
            '5:00'
        ]
        self.carregar_predefinicoes()

    def carregar_predefinicoes(self):
        try:
            path = resource_path_full('predefinicoes.json', 'configs')
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.predef_names = list(data.keys())
            else:
                self.predef_names = []
        except Exception as e:
            print(f"Erro ao carregar predefinições: {e}")
            self.predef_names = []



    def on_leave(self):
        App.get_running_app().unbind(cor_fundo=self.on_cor_fundo_change)

    def on_cor_fundo_change(self, instance, value):
        self.canvas.before.clear()
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*App.get_running_app().cor_fundo)
            Rectangle(pos=self.pos, size=self.size)

    def carregar_perguntas(self):
        db_file = get_db_filename(self.game_mode)
        try:
            with open(db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                perguntas = data.get('perguntas', [])
                self.ids.question_list.clear_widgets()
                for index, pergunta in enumerate(perguntas):
                    pergunta_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
                    pergunta_label = Label(text=pergunta['pergunta'], halign='left', valign='middle',font_size=dp(18))
                    pergunta_label.bind(size=pergunta_label.setter('text_size'))
                    editar_btn = Factory.ImageButtonEditar()
                    editar_btn.bind(on_press=lambda instance, idx=index: self.editar_pergunta(idx))
                    pergunta_box.add_widget(pergunta_label)
                    pergunta_box.add_widget(editar_btn)
                    self.ids.question_list.add_widget(pergunta_box)
        except FileNotFoundError:
            show_message_popup("Erro", "Arquivo de perguntas não encontrado.")

    def carregar_areas(self):
        db_file = get_db_filename(self.game_mode)
        try:
            with open(db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                areas = list(data.get('areas', {}).keys())
                self.available_areas = areas
        except FileNotFoundError:
            self.available_areas = []
            show_message_popup("Erro", "Arquivo de perguntas não encontrado.")
        except json.JSONDecodeError:
            self.available_areas = []
            show_message_popup("Erro", "Erro ao ler o arquivo de perguntas.")

    def editar_pergunta(self, question_index):
        add_edit_screen = self.manager.get_screen('add_edit_question')
        add_edit_screen.load_question_for_editing(question_index)
        self.manager.current = 'add_edit_question'

    def apply_filters(self):
        selected_area = self.ids.spinner_area_filter.text
        selected_difficulty = self.ids.spinner_difficulty_filter.text
        db_file = get_db_filename(self.game_mode)
        try:
            with open(db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                perguntas = data.get('perguntas', [])
                self.ids.question_list.clear_widgets()
                for index, pergunta in enumerate(perguntas):
                    area_ok = (selected_area == 'Todas') or (pergunta['area'] == selected_area)
                    difficulty_ok = (selected_difficulty == 'Todas') or (pergunta['dificuldade'].capitalize() == selected_difficulty)
                    if area_ok and difficulty_ok:
                        pergunta_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
                        pergunta_label = Label(text=pergunta['pergunta'], halign='left', valign='middle',font_size=dp(18))
                        pergunta_label.bind(size=pergunta_label.setter('text_size'))
                        editar_btn = Factory.ImageButtonEditar()
                        editar_btn.bind(on_press=lambda instance, idx=index: self.editar_pergunta(idx))

                        pergunta_box.add_widget(pergunta_label)
                        pergunta_box.add_widget(editar_btn)
                        self.ids.question_list.add_widget(pergunta_box)
        except FileNotFoundError:
            show_message_popup("Erro", "Arquivo de perguntas não encontrado.")
            
    def get_button_pos(self, btn_id, default_x, default_y):
        path = resource_path_full('posicoes_botoes_inicial.json', 'configs')
        data = load_json_cached(path, default={}) or {}
        if btn_id in data:
            return ajustar_posicao_letterbox(data[btn_id])
        
        # Novo cálculo para posição padrão com letterbox
        largura_viewport, altura_viewport, offset_x, offset_y = calcular_viewport()
        return [offset_x + default_x * largura_viewport, offset_y + default_y * altura_viewport]
        
    def salvar_todas_posicoes(self):
        botoes = [
            'spinner_game_mode_list',
            'spinner_area_filter',
            'spinner_difficulty_filter',
            'btn_voltar_listar',
        ]
        data = {}
        for btn_id in botoes:
            if btn_id in self.ids:
                data[btn_id] = self.ids[btn_id].pos
        path = resource_path_full('posicoes_botoes_listar.json', 'configs')
        with open(path, "w") as f:
            json.dump(data, f)

    def carregar_posicoes(self):
        path = resource_path_full('posicoes_botoes_listar.json', 'configs')
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
            for btn_id, pos in data.items():
                print(f"[DEBUG] Resolução atual da janela- botoes listat: {Window.width}x{Window.height}")
                if btn_id in self.ids:
                    self.ids[btn_id].pos = pos



class VideoScreen(Screen):
    video_path = StringProperty(resource_path_full('transição roleta.mp4', 'assets'))

    def on_enter(self):
        # toca o vídeo e já prepara a tela do jogo em background
        self.ids.video.state = 'play'
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self._preload_jogo(), 0.1)

    def _preload_jogo(self, *args):
        try:
            tela = self.manager.get_screen('tela_jogo')
            if hasattr(tela, 'preparar_jogo_rapido'):
                tela.preparar_jogo_rapido()
        except Exception as e:
            print('[preload] erro:', e)

    def on_video_end(self, instance, value):
        # descarrega o vídeo e troca de tela sem travar
        from kivy.clock import Clock
        v = self.ids.video
        try:
            v.state = 'stop'
            v.source = ''
            if hasattr(v, 'unload'):
                v.unload()
        except Exception as e:
            print('[video end] unload fail:', e)

        Window.set_icon(resource_path_full('icone.ico', 'assets'))
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'tela_jogo'), 0)



class RoletaApp(App):
    
    game_started_once = False
    cor_fundo = ListProperty([0.25, 0.12, 0.05, 1])
    Window.title = "Roleta Química"
    Window.set_icon(resource_path_full('icone.ico', 'assets'))
    musica_fundo = None  # 🔈 Aqui guardamos a música
    
    
    def build(self):
        Window.maximize()
        Window.set_title('Roleta Química')
        Window.set_icon(resource_path_full('icone.ico', 'assets'))  # coloque dentro do build
        self.carregar_cor_fundo()
        ajustar_posicoes_para_tela()
        Window.size = (1366, 705)
        print(f"[DEBUG] Tamanho da janela forçado: {Window.size}")
        
        # 🔈 Carregar e tocar a música de fundo (dentro do build)
        self.musica_fundo = SoundLoader.load(resource_path_full('musicadefundo extendida (Remix).mp3', 'sons'))
        if self.musica_fundo:
            initial = 0.1  # volume inicial (ou o que você quiser)
            self.musica_fundo.loop = True
            self.musica_fundo.volume = initial
            self.musica_fundo.play()

            # 🔧 Alguns providers resetam o volume depois do play; reforça no próximo frame
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: setattr(self.musica_fundo, 'volume', initial), 0)



        self.som_acerto = SoundLoader.load(resource_path_full('copoenchendo.mp3', 'sons'))
        if self.som_acerto:
            self.som_acerto.volume = 1  # Volume entre 0.0 (mudo) e 1.0 (máximo)

        self.som_erro = SoundLoader.load(resource_path_full('copo quebrando.mp3', 'sons'))
        if self.som_erro:
            self.som_erro.volume = 1         
        sm = ScreenManager()
        sm.add_widget(LoadingScreen(name='loading_screen'))
        sm.add_widget(TelaIntroducao(name='intro_screen'))
        sm.add_widget(TelaInicial(name='tela_inicial'))
        sm.add_widget(TelaJogo(name='tela_jogo'))
        sm.add_widget(AddEditQuestionScreen(name='add_edit_question'))
        sm.add_widget(QuestionListScreen(name='question_list'))
        sm.add_widget(VideoScreen(name='video_screen'))  # Nova tela para o vídeo
        sm.add_widget(TelaPredefinicao(name='tela_predefinicao'))
        sm.add_widget(HistoricoScreen(name='historico_screen'))
        sm.add_widget(TelaCreditos(name='tela_creditos'))

        sm.current = 'loading_screen'
        return sm
    
    def on_start(self):
        Window.set_title('Roleta Química')  # <- AQUI! depois que tudo carregou
        Window.set_icon(resource_path_full('icone.ico', 'assets'))
    def on_stop(self):
        self.salvar_cor_fundo()

    def carregar_cor_fundo(self):
        try:
            with open(resource_path_full('config.json', 'configs'), 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.cor_fundo = config.get('cor_fundo', [0.00, 0.50, 0.50, 1])
                Window.clearcolor = self.cor_fundo
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def salvar_cor_fundo(self):
        config = {'cor_fundo': self.cor_fundo}
        try:
            with open(resource_path_full('config.json', 'configs'), 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            pass

    def save_button_position(self, btn_id, pos):
        """Salva a posição de um botão arrastado na introdução."""
        path = resource_path_full('posicoes_botoes.json', 'configs')
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
        data[btn_id] = pos
        with open(path, "w") as f:
            json.dump(data, f)

if __name__ == '__main__':
    Window.set_icon(resource_path_full('icone.ico', 'assets'))
    #threading.Thread(target=hover_loop, daemon=True).start()
    RoletaApp().run()



    def prepare_data(self):
        try:
            # Carrega o modo atual e abre o JSON correspondente
            base = os.path.abspath("."); configs = os.path.join(base, "")
            dbs = ["dataperguntas1ano_bncc.json","dataperguntas2ano_bncc.json","dataperguntas3ano_bncc.json","dataperguntas_coffeelovers.json"]
            items = []
            for fn in dbs:
                path = os.path.join(configs, fn)
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        banco = json.load(f)
                    for area, perguntas in banco.items():
                        for p in perguntas:
                            items.append({'area': area, 'dificuldade': p.get('dificuldade',''), 'pergunta': p.get('pergunta','')})
            self._pending_items = items
        except Exception:
            self._pending_items = []

    def start_chunked_build(self):
        from kivy.clock import Clock
        layout = getattr(self.ids, 'lista_perguntas_layout', None) or getattr(self.ids, 'perguntas_layout', None)
        if not layout:
            return
        items = self._pending_items or []
        if not items:
            return
        layout.clear_widgets()
        batch = 30
        data_iter = iter(items)
        def _step(dt):
            added = 0
            from kivy.uix.label import Label
            while added < batch:
                try:
                    item = next(data_iter)
                except StopIteration:
                    self._build_ev.cancel()
                    return
                lbl = Label(text=f"[{item.get('dificuldade','')}] {item.get('area','')}: {item.get('pergunta','')}", size_hint_y=None, height=dp(28))
                layout.add_widget(lbl)
                added += 1
        if self._build_ev:
            try: self._build_ev.cancel()
            except Exception: pass
        self._build_ev = Clock.schedule_interval(_step, 0)
