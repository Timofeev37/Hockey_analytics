import pandas as pd
from PIL import Image
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def generate(order):
    df = pd.read_csv(r'static\csv\best_goalies.csv', index_col=0)
    print(order)
    if order == '10 худших вратарей по GSAx':
        df = df.tail(10)
    else:
        df = df.head(10)

    # Определение размеров и цветов
    n_rows, n_cols = df.shape
    col_widths = [0.025, 0.085, 0.15, 0.115, 0.075, 0.075, 0.075, 0.055, 0.085, 0.075, 0.085]
    row_height = 0.04
    x_coords = [0] * n_cols
    y_coords = [0] * (n_rows + 1)
    x_text_margin = 0.015
    y_text_margin = 0.01

    # Вычисляем координаты X для каждого столбца
    x_pos = 0
    for i in range(n_cols):
        x_coords[i] = x_pos
        x_pos += col_widths[i]
    max_x = x_pos
    print(x_pos)
    # Вычисляем координаты Y для каждой строки
    y_pos = 0.95
    for i in range(n_rows + 1):
        y_coords[i] = y_pos
        y_pos -= row_height

    # Создаем фигуру и оси
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')
    ax.set_facecolor('none')  # ЭТА СТРОКА ДЕЛАЕТ ФОН ПРОЗРАЧНЫМ
    fig.patch.set_alpha(0)

    # Отрисовка заголовков столбцов
    for j, col in enumerate(df.columns):
        x_pos = x_coords[j] + col_widths[j] / 2 if col != 'Игрок' else x_coords[j]
        y_pos = y_coords[0] - row_height / 2
        ax.text(x_pos, y_pos, col if (col != 'link' and col != '#') else "",
                fontsize=12,
                fontweight='bold',
                ha='center' if col != 'Игрок' else 'left',
                va='center')

        # Рисуем фон для заголовка
        ax.add_patch(plt.Rectangle((x_coords[j], y_coords[0] - row_height), col_widths[j], row_height,
                                   edgecolor='none', facecolor='#f9f9f9'))
    zorder = 0
    # Отрисовка данных и горизонтальных линий
    for i, (idx, row) in enumerate(df.iterrows()):
        y_pos = y_coords[i + 1] - row_height / 2

        # Рисуем фон для строк данных
        bg_color = '#f9f9f9' if i % 2 == 0 else '#f9f9f9'
        ax.add_patch(plt.Rectangle((0, y_coords[i + 1] - row_height), max_x, row_height,
                                   edgecolor='none', facecolor=bg_color))

        # Рисуем тонкую горизонтальную линию
        ax.plot([0.0, max_x], [y_coords[i + 1], y_coords[i + 1]], c='lightgray', lw=0.5, zorder=1)

        # Отрисовка текста или изображения
        for j, val in enumerate(row):
            x_pos = x_coords[j] + col_widths[j] / 2 if j != df.columns.get_loc('Игрок') else x_coords[j]

            # Если это первый столбец, вставляем изображение
            if j == 1:
                zorder += 1
                link = str(val)
                photo_path = os.path.join(r'static\images\players', f'{link}.png')

                # Координаты ячейки
                left = x_coords[j]
                right = x_coords[j] + col_widths[j]
                bottom = y_coords[i + 1] - row_height
                top = y_coords[i + 1]

                if os.path.exists(photo_path):
                    img = Image.open(photo_path)
                    w, h = img.size

                    # Сохраняем пропорции
                    cell_aspect = col_widths[j] / row_height
                    image_aspect = w / h

                    if image_aspect > cell_aspect:
                        # Если изображение шире ячейки, масштабируем по ширине
                        new_w = 1.2 * w * (col_widths[j] / w)
                        new_h = 1.2 * h * (col_widths[j] / w)
                    else:
                        # Если изображение выше ячейки, масштабируем по высоте
                        new_w = 1.2 * w * (row_height / h)
                        new_h = 1.2 * h * (row_height / h)

                    # Вычисляем новые координаты для центрирования изображения
                    image_left = x_coords[j] + (col_widths[j] - new_w) / 2
                    image_bottom = y_coords[i + 1] - row_height

                    # Вставляем изображение с правильными координатами
                    ax.imshow(np.array(img),
                              extent=(image_left, image_left + new_w, image_bottom, image_bottom + new_h),
                              aspect='auto',
                              zorder=zorder + 1)

                else:
                    # Если файл не найден, просто выводим имя игрока
                    ax.text(x_pos, y_pos, str(val),
                            fontsize=9, color='black', ha='center', va='center')


            # Для остальных столбцов отрисовываем текст
            else:
                text_color = 'black'
                font_size = 10
                font_weight = 'normal'

                if j == df.columns.get_loc('GSAx'):
                    font_weight = 'bold'
                    text_color = 'red' if val < 0 else 'green'
                    font_size = 11

                ax.text(x_pos, y_pos, str(val),
                        fontsize=font_size,
                        fontweight=font_weight,
                        color=text_color,
                        ha='center' if j != df.columns.get_loc('Игрок') else 'left',
                        va='center')

    # Добавляем толстую разделительную линию под заголовком
    ax.plot([0, max_x], [y_coords[1], y_coords[1]], c='black', lw=1.5, zorder=1)

    # Добавляем самую нижнюю линию
    ax.plot([0, max_x], [y_coords[n_rows] - row_height, y_coords[n_rows] - row_height], c='lightgray', lw=0.5, zorder=1)

    # plt.show()
    filename = f'best_goalies.png'
    output_path = r'static\images'
    output_path = os.path.join(output_path, filename)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')