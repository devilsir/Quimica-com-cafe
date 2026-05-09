import json
import os
import sys
from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.uix.behaviors import DragBehavior
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.app import App
from kivy.uix.spinner import Spinner
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, StringProperty

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
# 📦 Definir base_path correto (se .exe, usa pasta do exe)
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.abspath(os.path.dirname(__file__))


def show_message_popup(title, message):
    from telas_e_botoes import show_message_popup as main_popup
    return main_popup(title, message)


class DraggableSpinner(DragBehavior, Spinner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drag_rectangle = [0, 0, self.width, self.height]
        self.drag_timeout = 10000000
        self.drag_distance = 0
        self._drag_enabled = False

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            tela = App.get_running_app().root.get_screen('tela_predefinicao')
            self._drag_enabled = hasattr(tela, 'arraste_liberado') and tela.arraste_liberado
            if self._drag_enabled:
                self.drag_rectangle = [self.x, self.y, self.width, self.height]
                return super().on_touch_down(touch)
            else:
                return super().on_touch_down(touch)
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._drag_enabled:
            return super().on_touch_move(touch)
        return False

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            tela = App.get_running_app().root.get_screen('tela_predefinicao')
            if hasattr(tela, 'salvar_posicoes'):
                for id_name, widget in tela.ids.items():
                    if widget is self:
                        tela.posicoes_botoes[id_name] = list(self.pos)
                        break
        return super().on_touch_up(touch)



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

        Window.bind(mouse_pos=self.on_mouse_pos)
        self.update_sources()

    def on_kv_post(self, base_widget):
        self.update_sources()

    def update_sources(self):
        self.source_normal = self.source or self.source_normal
        self.source_hover = self._add_suffix(self.source_normal, '_hover')
        self.source_down = self._add_suffix(self.source_normal, '_hover')
        self.image.source = self.source_normal
        self.label.text = self.text

    def _add_suffix(self, filename, suffix):
        name, ext = os.path.splitext(filename)
        return f"{name}{suffix}{ext}" if ext.lower() in ['.png', '.jpg', '.jpeg', '.webp'] else filename

    def on_mouse_pos(self, window, pos):
        if not self.get_root_window():
            return
        inside = self.collide_point(*self.to_widget(*pos))
        if inside and os.path.exists(self.source_hover):
            self.image.source = self.source_hover
        else:
            self.image.source = self.source_normal

    def on_press(self):
        if os.path.exists(self.source_down):
            self.image.source = self.source_down

    def on_release(self):
        pos = Window.mouse_pos
        if self.get_root_window() and self.collide_point(*self.to_widget(*pos)) and os.path.exists(self.source_hover):
            self.image.source = self.source_hover
        else:
            self.image.source = self.source_normal
Builder.load_string('''#:import resource_path_full predefinicoes.resource_path_full


<CustomSpinnerOptionInicial@SpinnerOption>:
    background_normal: resource_path_full('botao generico telainicial.png', 'assets')
    background_down: resource_path_full('botao generico telainicial_hover.png', 'assets')
    color: 1, 1, 1, 1
    font_size: dp(20)
    
<TelaPredefinicao>:
    name: 'tela_predefinicao'
    FloatLayout:
        Image:
            source: resource_path_full('fundo generico2.jpg', 'assets')
            allow_stretch: True
            keep_ratio: False
            size_hint: 1, 1

        # --- SPINNERS EMPILHADOS NO TOPO ---
        DraggableSpinner:
            id: spinner_predefinicao
            option_cls: 'CustomSpinnerOptionInicial'
            text: 'Escolher Predefinição'
            values: root.predef_names
            background_normal: resource_path_full('botao generico telainicial.png', 'assets')
            background_down: resource_path_full('botao generico telainicial.png', 'assets')
            size_hint: None, None
            size: dp(250), dp(60)
            pos_hint: {'center_x': 0.25, 'top': 0.80}
            on_text: root.carregar_predefinicao(self.text)

        DraggableSpinner:
            id: spinner_game_mode
            option_cls: 'CustomSpinnerOptionInicial'
            text: 'Todas'
            values: ['Todas'] + root.modos
            background_normal: resource_path_full('botao generico telainicial.png', 'assets')
            background_down: resource_path_full('botao generico telainicial.png', 'assets')
            size_hint: None, None
            size: dp(200), dp(60)
            pos_hint: {'center_x': 0.5, 'top': 0.80}
            on_text: root.on_modo_changed(self.text)

        DraggableSpinner:
            id: spinner_areas
            option_cls: 'CustomSpinnerOptionInicial'
            text: 'Todas'
            values: ['Todas'] + root.available_areas
            background_normal: resource_path_full('botao generico telainicial.png', 'assets')
            background_down: resource_path_full('botao generico telainicial.png', 'assets')
            size_hint: None, None
            size: dp(200), dp(60)
            pos_hint: {'center_x': 0.7, 'top': 0.80}
            on_text: root.filtrar_perguntas()

        DraggableSpinner:
            id: spinner_dificuldade
            option_cls: 'CustomSpinnerOptionInicial'
            text: 'Todas'
            values: ['Todas'] + root.available_difficulties
            background_normal: resource_path_full('botao generico telainicial.png', 'assets')
            background_down: resource_path_full('botao generico telainicial.png', 'assets')
            size_hint: None, None
            size: dp(200), dp(60)
            pos_hint: {'center_x': 0.9, 'top': 0.80}
            on_text: root.filtrar_perguntas()


        # --- SCROLLVIEW OCUPANDO O MEIO ---
        ScrollView:
            size_hint: 0.95, 0.50
            pos_hint: {'center_x': 0.5, 'center_y': 0.40}
            bar_width: dp(30)

            BoxLayout:
                id: perguntas_layout
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(10)
                padding: dp(10)

        # --- BOTÃO DE SALVAR FIXADO EMBAIXO ---
        HoverDraggableImageTextButton:
            text: 'Salvar Predefinição'
            size_hint: None, None
            size: dp(250), dp(60)
            pos_hint: {'center_x': 0.5, 'y': 0.02}
            source: resource_path_full('botao generico telainicial.png', 'assets')
            source_normal: resource_path_full('botao generico telainicial.png', 'assets')
            source_hover: resource_path_full('botao generico telainicial_hover.png', 'assets')
            source_down: resource_path_full('botao generico telainicial_hover.png', 'assets')
            on_press: root.popup_nome_predefinicao()

        # --- BOTÕES AUXILIARES (opcionalmente posicionáveis) ---
        HoverDraggableImageButton:
            id: btn_voltar
            source: resource_path_full('setavoltar.png', 'assets')
            source_normal: resource_path_full('setavoltar.png', 'assets')
            source_hover: resource_path_full('setavoltar_hover.png', 'assets')
            source_down: resource_path_full('setavoltar_hover.png', 'assets')
            size_hint: None, None
            size: dp(60), dp(60)
            pos_hint: {'center_x': 0.1, 'y': 0.8}
            pos: root.posicoes_botoes.get('btn_voltar', [dp(10), dp(10)])
            on_release:
                app.root.current = 'tela_inicial'


''')

class TelaPredefinicao(Screen):
    modos = ListProperty(['1º ano', '2º ano', '3º ano', 'Coffee Lovers'])
    available_areas = ListProperty([])
    available_difficulties = ListProperty(['Fácil', 'Médio', 'Difícil'])
    predef_names = ListProperty([])
    game_mode = StringProperty('Todas')

    perguntas_filtradas = ListProperty([])
    todas_perguntas = ListProperty([])
    checkboxes = []

    posicoes_botoes = {}

    def on_pre_enter(self):
        self.carregar_posicoes()
        self.ids.spinner_game_mode.text = self.game_mode
        self.carregar_predefs()
        self.on_modo_changed(self.game_mode)


    def salvar_posicoes(self):
        try:
            for id_name in ['btn_voltar', 'btn_salvar_pos', 'btn_fake1', 'btn_fake2', 'btn_fake3', 'btn_fake4','btn_voltar', 'btn_salvar_pos',
            'spinner_predefinicao', 'spinner_game_mode',
            'spinner_areas', 'spinner_dificuldade']:
                widget = self.ids.get(id_name)
                if widget:
                    self.posicoes_botoes[id_name] = list(widget.pos)

            path = resource_path_full('posicoes_predefinicoes.json', 'configs')
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.posicoes_botoes, f, indent=4)
            show_message_popup("Sucesso", "Posições salvas!")
        except Exception as e:
            show_message_popup("Erro", f"Erro ao salvar posições: {e}")


    def carregar_posicoes(self):
        try:
            path = resource_path_full('posicoes_predefinicoes.json', 'configs')
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    self.posicoes_botoes = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar posições: {e}")
            self.posicoes_botoes = {}


    def carregar_predefs(self):
        path = resource_path_full('predefinicoes.json', 'configs')
        if not os.path.exists(path):
            self.predef_names = []
            return
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.predef_data = data
        self.predef_names = list(data.keys())

    def carregar_predefinicao(self, nome):
        if nome not in self.predef_data:
            return
        perguntas = self.predef_data[nome].get("perguntas", [])
        self.ids.spinner_game_mode.text = self.predef_data[nome].get("modo", "Todas")
        self.on_modo_changed(self.game_mode)
        self.perguntas_filtradas = perguntas
        self.atualizar_layout_perguntas(preselecionadas=True)

    def on_modo_changed(self, modo):
        self.game_mode = modo
        self.carregar_perguntas()
        self.filtrar_perguntas()

    def carregar_perguntas(self):
        self.todas_perguntas = []
        all_areas = set()

        modos_arquivos = {
            '1º ano': 'dataperguntas1ano.json',
            '2º ano': 'dataperguntas2ano.json',
            '3º ano': 'dataperguntas3ano.json',
            'Coffee Lovers': 'dataperguntas.json'
        }

        modos_a_carregar = self.modos if self.game_mode == 'Todas' else [self.game_mode]

        for modo in modos_a_carregar:
            try:
                caminho = resource_path_full(modos_arquivos[modo], 'configs')
                with open(caminho, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    perguntas = data.get('perguntas', [])
                    for pergunta in perguntas:
                        pergunta['_modo'] = modo
                        self.todas_perguntas.append(pergunta)
                    all_areas.update(data.get('areas', {}).keys())
            except Exception as e:
                print(f"[ERRO] Ao carregar perguntas do modo '{modo}': {e}")
                continue


        self.available_areas = sorted(list(all_areas))

    def filtrar_perguntas(self):
        area = self.ids.spinner_areas.text
        dificuldade = self.ids.spinner_dificuldade.text

        perguntas = self.todas_perguntas
        if area != 'Todas':
            perguntas = [p for p in perguntas if p.get('area') == area]
        if dificuldade != 'Todas':
            perguntas = [p for p in perguntas if p.get('dificuldade', '').capitalize() == dificuldade]

        self.perguntas_filtradas = perguntas
        self.atualizar_layout_perguntas()

    def atualizar_layout_perguntas(self, preselecionadas=False):
        layout = self.ids.perguntas_layout
        layout.clear_widgets()
        self.checkboxes = []

        for pergunta in self.perguntas_filtradas:
            box = BoxLayout(
                size_hint_y=None,
                height=dp(60),
                spacing=dp(10),
                padding=[dp(10), 0],
            )

            checkbox = CheckBox(size_hint=(None, None), size=(dp(30), dp(30)))

            if preselecionadas:
                checkbox.active = True

            texto = f"[{pergunta.get('_modo', '')}] {pergunta.get('pergunta', 'Sem texto')}"
            label = Label(
                text=texto,
                halign='left',
                valign='middle',
                font_size=dp(18),
                size_hint_x=1
            )
            label.bind(size=label.setter('text_size'))

            box.add_widget(checkbox)
            box.add_widget(label)
            layout.add_widget(box)
            self.checkboxes.append((checkbox, pergunta))



    def popup_nome_predefinicao(self):
        box = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        input_nome = TextInput(multiline=False, size_hint=(1, None), height=dp(50))
        btn_salvar = Button(text="Salvar", size_hint_y=None, height=dp(40),background_normal=resource_path_full('botao generico popup generico.png', 'assets'),background_down=resource_path_full('botao generico popup generico.png', 'assets'),)
        box.add_widget(Label(text="Digite o nome da predefinição:", font_size= dp (15)))
        box.add_widget(input_nome)
        box.add_widget(btn_salvar)

        popup = Popup(title='', separator_height=0,content=box,
                      size_hint=(None, None), size=(dp(400), dp(200)))

        def salvar_nome(_):
            nome = input_nome.text.strip()
            if not nome:
                show_message_popup("Erro", "Digite um nome válido.")
                return
            popup.dismiss()
            self.salvar_predefinicao_com_nome(nome)

        btn_salvar.bind(on_press=salvar_nome)
        popup.open()

    def salvar_predefinicao_com_nome(self, nome):
        perguntas_selecionadas = [
            pergunta for checkbox, pergunta in self.checkboxes if checkbox.active
        ]

        if not perguntas_selecionadas:
            show_message_popup("Erro", "Selecione ao menos uma pergunta.")
            return

        try:
            path = resource_path_full('predefinicoes.json', 'configs')
            predefinicoes = {}
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    predefinicoes = json.load(f)

            predefinicoes[nome] = {
                'modo': self.game_mode,
                'perguntas': perguntas_selecionadas
            }

            with open(path, 'w', encoding='utf-8') as f:
                json.dump(predefinicoes, f, ensure_ascii=False, indent=4)

            show_message_popup("Sucesso", "Predefinição salva com sucesso!")
            self.carregar_predefs()
        except Exception as e:
            show_message_popup("Erro", f"Erro ao salvar: {e}")
