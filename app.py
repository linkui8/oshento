from flask import Flask, render_template, request
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import io
import base64
import tempfile
import os
import time
from functools import lru_cache
from models import Man

app = Flask(__name__)

# Кэшируем анимацию
@lru_cache(maxsize=32)
def create_animation(transition_times=None):
    start_time = time.time()
    
    # Параметры анимации
    total_frames = 40
    fps = 8
    
    # Если переданы времена переходов, конвертируем их в кадры
    if transition_times:
        transition_speeds = {
            'Рот-Желудок': int(transition_times[0] * fps),
            'Желудок-Печень': int(transition_times[1] * fps),
            'Печень-Сердце': int(transition_times[2] * fps),
            'Сердце-Органы': int(transition_times[2] * fps)  # Используем время до сердца для последнего перехода
        }
        total_frames = sum(transition_speeds.values()) + 20  # Добавляем запас кадров для накопления
    else:
        transition_speeds = {
            'Рот-Желудок': 8,
            'Желудок-Печень': 12,
            'Печень-Сердце': 10,
            'Сердце-Органы': 10
        }
    
    # Создаем фигуру
    fig, ax = plt.subplots(figsize=(12, 6))
    plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
    
    # Органы в порядке поражения (x, y, width, height)
    organs = [
        {'name': 'Рот', 'pos': (0.1, 0.5, 0.1, 0.15), 'order': 1, 'color': '#FFDDC1'},
        {'name': 'Желудок', 'pos': (0.3, 0.5, 0.15, 0.2), 'order': 2, 'color': '#FFABAB'},
        {'name': 'Печень', 'pos': (0.5, 0.5, 0.18, 0.25), 'order': 3, 'color': '#FFC3A0'},
        {'name': 'Сердце', 'pos': (0.75, 0.5, 0.15, 0.18), 'order': 4, 'color': '#FF677D'},
        {'name': 'Органы', 'pos': (0.9, 0.5, 0.1, 0.3), 'order': 5, 'color': '#D4A5A5'}
    ]
    
    # Рисуем органы
    for organ in organs:
        x, y, w, h = organ['pos']
        ax.add_patch(plt.Rectangle(
            (x-w/2, y-h/2), w, h, 
            fill=True, color=organ['color'], 
            ec='black', lw=2, alpha=0.8
        ))
        ax.text(x, y, organ['name'], 
               ha='center', va='center', 
               fontsize=10, weight='bold')
    
    # Рисуем сосуды между органами
    vessel_points = []
    for i in range(len(organs)-1):
        x1 = organs[i]['pos'][0] + organs[i]['pos'][2]/2
        x2 = organs[i+1]['pos'][0] - organs[i+1]['pos'][2]/2
        y = organs[i]['pos'][1]
        ax.plot([x1, x2], [y, y], 'r-', lw=3, alpha=0.4, color='#555555')
        vessel_points.append((x1, x2, y))
    
    # Настройки графика
    ax.set_xlim(0, 1)
    ax.set_ylim(0.2, 0.8)
    ax.axis('off')
    ax.set_title('Распространение синильной кислоты (HCN) в организме', pad=20)
    
    # Глобальные переменные для анимации
    current_transition = None
    transition_start_frame = 0
    particles = []
    
    def update(frame):
        nonlocal current_transition, transition_start_frame, particles
        
        # Очищаем предыдущие элементы
        while len(ax.collections) > 0:
            ax.collections[0].remove()
        
        # Определяем текущую фазу распространения
        progress = frame / total_frames
        
        # 1. Показываем накопление в текущем органе
        for i, organ in enumerate(organs):
            if frame >= sum(list(transition_speeds.values())[:i]) + i*5:  # Орган уже поражен
                x, y, w, h = organ['pos']
                num_points = min(15, int(15 * (frame - (sum(list(transition_speeds.values())[:i]) + i*5)) / 5))
                
                # Генерируем точки внутри органа
                points_x = x - w/2 + w * np.random.rand(num_points)
                points_y = y - h/2 + h * np.random.rand(num_points)
                sizes = np.random.uniform(20, 50, num_points)
                colors = [(1, 0.8 - 0.7*i/len(organs), 0.8 - 0.7*i/len(organs))] * num_points
                
                ax.scatter(points_x, points_y, s=sizes, c=colors, alpha=0.7)
        
        # 2. Показываем переход между органами
        cumulative_frames = 0
        for i in range(len(organs)-1):
            start_frame = cumulative_frames + i*5
            end_frame = start_frame + transition_speeds[f"{organs[i]['name']}-{organs[i+1]['name']}"]
            cumulative_frames += transition_speeds[f"{organs[i]['name']}-{organs[i+1]['name']}"]
            
            if start_frame <= frame <= end_frame:
                x1, x2, y = vessel_points[i]
                progress = (frame - start_frame) / (end_frame - start_frame)
                px = x1 + (x2 - x1) * progress
                
                # Рисуем движущуюся частицу
                ax.scatter([px], [y], s=100, c='red', alpha=0.8)
                
                # Рисуем след
                trail_x = np.linspace(x1, px, 10)
                trail_y = [y] * 10
                ax.scatter(trail_x, trail_y, s=np.linspace(10, 50, 10), 
                          c='pink', alpha=np.linspace(0.2, 0.8, 10))
        
        return ax.collections
    
    # Сохраняем анимацию во временный файл
    with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as tmpfile:
        temp_filename = tmpfile.name
    
    # Создаем анимацию
    anim = FuncAnimation(fig, update, frames=total_frames, interval=100, blit=False)
    
    # Оптимизированные параметры сохранения
    anim.save(temp_filename, writer='pillow', fps=fps, dpi=80,
             savefig_kwargs={'facecolor': 'white'},
             progress_callback=lambda i, n: print(f'Сохранение кадра {i}/{n}') if i % 10 == 0 else None)
    
    plt.close(fig)
    
    # Читаем и кодируем GIF
    with open(temp_filename, 'rb') as f:
        video_data = base64.b64encode(f.read()).decode('utf-8')
    
    os.unlink(temp_filename)
    print(f"Анимация создана за {time.time()-start_time:.2f} сек")
    return video_data

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    transition_times = None
    if request.method == 'POST':
        try:
            weight = float(request.form.get('weight'))
            amount = float(request.form.get('amount'))
            toxin_type = request.form.get('toxin_type', 'apple')
            man = Man(weight, amount, toxin_type)
            result = man.death()
            # Extract transition times from bpmj
            # bpmj keys: 1,2,3 with [distance, time, speed]
            from config import bpmj
            transition_times = [bpmj[1][1], bpmj[2][1], bpmj[3][1]]
        except Exception as e:
            result = f"Ошибка при обработке данных: {e}"
    animation = create_animation(tuple(transition_times) if transition_times else None)
    return render_template('index.html', animation=animation, result=result)

if __name__ == '__main__':
    app.run(debug=True, host="192.168.208.50")
