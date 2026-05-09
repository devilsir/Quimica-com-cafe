import json, math, sys, os, random
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Ellipse
from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty, StringProperty
from kivy.event import EventDispatcher

def resource_path_full(relative_path, subfolder=""):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    if subfolder:
        return os.path.join(base_path, subfolder, relative_path)
    return os.path.join(base_path, relative_path)

class RotatingWheel(FloatLayout, EventDispatcher):
    angle = NumericProperty(0)
    is_animating = False
    speed = NumericProperty(0)
    segments = NumericProperty(0)
    segments_data = ListProperty([])
    selected_area = StringProperty("")

    area_names = ListProperty([])
    colors = ListProperty([])

    initial_speed = NumericProperty(0)
    acceleration_duration = NumericProperty(0)
    deceleration_duration = NumericProperty(0)
    acceleration_time = NumericProperty(0)
    deceleration_time = NumericProperty(0)
    state = StringProperty("idle")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_area_selected')
        self.bind(area_names=self.on_area_names_changed, colors=self.on_colors_changed)

        if not self.segments_data:
            self.load_data_from_json(resource_path_full('dataperguntas.json', 'configs'))
            if not self.segments_data:
                print("Nenhum dado carregado, usando dados padrão.")
                self.area_names = ["Default"]
                self.colors = [[1, 1, 1, 1]]
                self.update_segments_from_properties()

    def on_area_names_changed(self, instance, value):
        self.update_segments_from_properties()

    def on_colors_changed(self, instance, value):
        self.update_segments_from_properties()


    def update_segments_from_properties(self):
        if self.area_names and self.colors and len(self.area_names) > 0:
            # Pares (nome, cor) vindos da tela de jogo
            area_color_pairs = list(zip(self.area_names, self.colors))

            # Define quais nomes são considerados áreas especiais
            especiais = {"+5 pontos 1", "+5 pontos 2", "-5 pontos 1", "-5 pontos 2"}

            # Separa em listas de áreas especiais e normais
            special_pairs = [p for p in area_color_pairs if p[0] in especiais]
            normal_pairs = [p for p in area_color_pairs if p[0] not in especiais]

            total_special = len(special_pairs)
            total_normal = len(normal_pairs)
            total = len(area_color_pairs)

            # Se não tem nenhuma área especial, só embaralha tudo e mantém pesos iguais
            if total_special == 0:
                random.shuffle(area_color_pairs)
                new_segments = []
                for nome, cor in area_color_pairs:
                    peso = 1
                    new_segments.append({
                        "nome": nome,
                        "cor": cor,
                        "peso": peso
                    })
                self.segments_data = new_segments
                self.segments = len(new_segments)
                return

            # Embaralha a ordem interna de especiais e normais
            random.shuffle(special_pairs)
            random.shuffle(normal_pairs)

            # Monta um vetor de posições e coloca as especiais espaçadas
            result_pairs = [None] * total
            step = float(total) / float(total_special)
            pos = 0.0

            for sp in special_pairs:
                idx = int(round(pos)) % total
                start_idx = idx
                # Procura o próximo slot vazio, se esse já estiver ocupado
                while result_pairs[idx] is not None:
                    idx = (idx + 1) % total
                    if idx == start_idx:
                        break
                result_pairs[idx] = sp
                pos += step

            # Preenche os buracos com as áreas normais
            normal_iter = iter(normal_pairs)
            for i in range(total):
                if result_pairs[i] is None:
                    try:
                        result_pairs[i] = next(normal_iter)
                    except StopIteration:
                        # Se por algum motivo acabar as normais, sai do loop
                        break

            # Agora calcula os pesos mantendo 10% para especiais e 90% para normais
            new_segments = []
            for nome, cor in result_pairs:
                if nome in especiais and total_special > 0:
                    peso = (1.0 / 10.0) / float(total_special)
                elif total_normal > 0:
                    peso = (9.0 / 10.0) / float(total_normal)
                else:
                    peso = 1.0
                new_segments.append({
                    "nome": nome,
                    "cor": cor,
                    "peso": peso
                })

            self.segments_data = new_segments
            self.segments = len(new_segments)


    def draw_segments(self):
        if not self.segments_data or self.segments == 0:
            return

        self.canvas.clear()
        with self.canvas:
            total_weight = sum(segment['peso'] for segment in self.segments_data)
            radius = min(self.width, self.height) / 2 * 0.9
            current_angle = 0
            angulo_atual = (-self.angle) % 360

            for segment in self.segments_data:
                angle_segment = (segment['peso'] / total_weight) * 360
                segment_center = current_angle + angle_segment / 2
                diff = abs(((angulo_atual - segment_center + 180) % 360) - 180)

                if diff <= angle_segment / 2:
                    highlight_color = self.brighten_color(segment['cor'], factor=1.5)
                    Color(*highlight_color)
                else:
                    Color(*segment['cor'])

                Ellipse(pos=(self.center_x - radius, self.center_y - radius),
                        size=(2 * radius, 2 * radius),
                        angle_start=current_angle,
                        angle_end=current_angle + angle_segment)

                current_angle += angle_segment

    def brighten_color(self, color, factor=1.2):
        return tuple(min(c * factor, 1) for c in color[:3]) + (color[3] if len(color) > 3 else 1,)

    def start_animation(self, initial_speed=300, acceleration_duration=2, deceleration_duration=5):
        if not self.is_animating:
            self.is_animating = True
            self.initial_speed = initial_speed
            self.acceleration_duration = acceleration_duration
            self.deceleration_duration = deceleration_duration
            self.speed = 0
            self.acceleration_time = 0
            self.deceleration_time = 0
            self.state = "accelerating"
            Clock.schedule_interval(self.update, 1 / 60)

    def update(self, dt):
        if not self.is_animating:
            return

        if self.state == "accelerating":
            self.acceleration_time += dt
            if self.acceleration_time < self.acceleration_duration:
                self.speed = (self.acceleration_time / self.acceleration_duration) * self.initial_speed
            else:
                self.state = "decelerating"
                self.deceleration_time = 0
                self.speed = self.initial_speed

        if self.state == "decelerating":
            self.deceleration_time += dt
            if self.deceleration_time < self.deceleration_duration:
                self.speed = self.initial_speed * (1 - (self.deceleration_time / self.deceleration_duration))
            else:
                self.speed = 0
                self.is_animating = False
                Clock.unschedule(self.update)
                self.check_area()

        self.angle += self.speed * dt
        self.angle %= 360
        self.update_canvas()

    def stop_animation(self):
        if self.is_animating:
            self.is_animating = False
            Clock.unschedule(self.update)
            self.check_area()

    def check_area(self):
        if not self.segments_data or self.segments == 0:
            return

        total_weight = sum(segment['peso'] for segment in self.segments_data)
        current_angle = 0

        # 🔄 Corrigido para usar o mesmo ângulo de referência que draw_segments
        angulo_final = (-self.angle) % 360
        selected_segment = None

        for segment in self.segments_data:
            angle_segment = (segment['peso'] / total_weight) * 360
            if current_angle <= angulo_final < current_angle + angle_segment:
                selected_segment = segment
                break
            current_angle += angle_segment

        if selected_segment:
            self.selected_area = selected_segment['nome']
            self.dispatch('on_area_selected', self.selected_area)

    def on_area_selected(self, segment_name):
        print(f'Evento disparado: Área selecionada é {segment_name}')

    def load_data_from_json(self, json_file_path):
        try:
            with open(resource_path_full(json_file_path), 'r', encoding='utf-8') as file:
                data = json.load(file)
                areas_data = data.get('areas', {})
                segments = []
                especiais = {"+5 pontos 1", "+5 pontos 2", "-5 pontos 1", "-5 pontos 2"}
                total_areas = len(areas_data)
                special_count = sum(1 for area in areas_data if area in especiais)
                normal_count = total_areas - special_count

                for area, color in areas_data.items():
                    if area in especiais and special_count > 0:
                        peso = (1/10) / special_count
                    elif normal_count > 0:
                        peso = (9/10) / normal_count
                    else:
                        peso = 1
                    segments.append({
                        'nome': area,
                        'cor': color,
                        'peso': peso
                    })

                self.segments_data = segments
                self.segments = len(segments)
        except FileNotFoundError:
            print(f"Arquivo {json_file_path} não encontrado.")
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {e}")

    def get_selected_segment(self):
        return self.selected_area

    def update_canvas(self):
        self.draw_segments()
