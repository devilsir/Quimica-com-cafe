import os, sys, json, glob
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.loader import Loader  # usar loader assíncrono p/ imagens
from kivy.app import App

def resource_path_full(relative_path, subfolder=""):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
    if subfolder:
        return os.path.join(base_path, subfolder, relative_path)
    return os.path.join(base_path, relative_path)

def _warm_fs(path: str, nbytes: int = 256 * 1024) -> None:
    """Aquece o cache do SO lendo um pedaço do arquivo sem instanciar decoders."""
    try:
        with open(path, "rb", buffering=0) as f:
            _ = f.read(nbytes)
    except Exception:
        pass

class LoadingScreen(Screen):
    def on_enter(self):
        # Prevent duplicate UI/timers when re-entering the screen
        if hasattr(self, '_ev') and self._ev:
            from kivy.clock import Clock as _Clock
            try:
                _Clock.unschedule(self._ev)
            except Exception:
                pass
            self._ev = None
        try:
            self.clear_widgets()
        except Exception:
            pass
        self._target_mode = True

        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.label = Label(text="Carregando recursos...", font_size='20sp')
        self.pb = ProgressBar(max=100, value=0)
        self.layout.add_widget(self.label)
        self.layout.add_widget(self.pb)
        self.add_widget(self.layout)

        # Build task list
        self.tasks = []

        # JSONs a pré-carregar
        json_files = [
            resource_path_full('posicoes_botoes_inicial.json', 'configs'),
            resource_path_full('posicoes_predefinicoes.json', 'configs'),
            resource_path_full('predefinicoes.json', 'configs'),
            resource_path_full('dataperguntas1ano.json', 'configs'),
            resource_path_full('dataperguntas2ano.json', 'configs'),
            resource_path_full('dataperguntas3ano.json', 'configs'),
            resource_path_full('dataperguntas.json', 'configs'),
        ]
        for jf in json_files:
            self.tasks.append(('json', jf))

        # Imagens comuns
        image_globs = [
            resource_path_full('*.png', 'assets'),
            resource_path_full('*.jpg', 'assets'),
            resource_path_full('*.jpeg', 'assets'),
            resource_path_full('*.webp', 'assets'),
        ]
        for pattern in image_globs:
            for fp in glob.glob(pattern):
                self.tasks.append(('image', fp))

        # Sons
        audio_ext = ['*.mp3', '*.wav', '*.ogg']
        for ext in audio_ext:
            for fp in glob.glob(resource_path_full(ext, 'sons')):
                self.tasks.append(('audio', fp))

        self.total = len(self.tasks) or 1
        self.done = 0

        # storage in App cache
        app = App.get_running_app()
        if not hasattr(app, 'cache'):
            app.cache = {'json': {}, 'images': set(), 'audio': set()}

        self._ev = Clock.schedule_interval(self._do_step, 0)

    def _do_step(self, dt):
        if self.done >= self.total:
            # finished basic resource loading
            Clock.unschedule(self._ev)
            app = App.get_running_app()

            # Se houver uma tela alvo, pré-carrega seus dados
            try:
                self._preload_target()
            except Exception:
                pass

            # Avança para a tela solicitada, se houver; senão, intro
            def go_next(*_):
                if app and app.root:
                    req = getattr(app, 'loading_request', None) or {}
                    nxt = req.get('target', 'intro_screen')
                    app.root.current = nxt
                    # Se a tela tem construção em chunks, dispare agora
                    try:
                        screen = app.root.get_screen(nxt)
                        if hasattr(screen, 'start_chunked_build'):
                            screen.start_chunked_build()
                    except Exception:
                        pass
            Clock.schedule_once(go_next, 0.1)
            return

        kind, path = self.tasks[self.done]
        app = App.get_running_app()
        try:
            if kind == 'json' and os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                app.cache['json'][path] = data

            elif kind == 'image' and os.path.exists(path):
                # usa Loader (assíncrono). Se falhar, aquece o FS.
                try:
                    Loader.load(path)
                    app.cache['images'].add(path)
                except Exception:
                    _warm_fs(path, 128 * 1024)

            elif kind == 'audio' and os.path.exists(path):
                # NUNCA instancie Sound aqui para não tocar/alterar mixer.
                _warm_fs(path, 256 * 1024)
                app.cache['audio'].add(path)

        except Exception:
            pass

        self.done += 1
        self.pb.value = int((self.done / self.total) * 100)
        self.label.text = f"Carregando recursos... {self.pb.value:.0f}%"

    def _preload_target(self):
        """Prepara dados para telas pesadas antes de entrar nelas."""
        app = App.get_running_app()
        req = getattr(app, 'loading_request', None) or {}
        target = req.get('target')
        if not target:
            return False
        try:
            sm = app.root
            screen = sm.get_screen(target)
        except Exception:
            return False

        # Chama prepare_data() se existir, para montar listas e caches
        prep_ok = True
        try:
            if hasattr(screen, 'prepare_data'):
                screen.prepare_data()
        except Exception:
            prep_ok = False

        # Marca que os dados já foram preparados; widgets serão criados em chunks ao entrar
        app._preload_ready = prep_ok
        return prep_ok

    def on_leave(self, *args):
        # Make sure nothing keeps running and remove old UI
        try:
            if hasattr(self, '_ev') and self._ev:
                Clock.unschedule(self._ev)
                self._ev = None
        except Exception:
            pass
        try:
            self.clear_widgets()
        except Exception:
            pass
