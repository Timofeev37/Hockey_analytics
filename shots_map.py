import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import seaborn as sns
import matplotlib.patches as patches
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)

def gg_rink(side="right", specs="nhl", ax=None):
    """
    Рисует хоккейную площадку (половину или полную) по стандартам NHL или IIHF.

    Args:
        side (str): Какую сторону нарисовать: "right" (по умолчанию) или "left".
                    "Right" = от центра до правой доски.
        specs (str): Какие спецификации использовать: "nhl" (по умолчанию) или "iihf".

    Returns:
        matplotlib.figure.Figure: Объект фигуры Matplotlib с нарисованной площадкой.
    """

    # --- Проверка входных данных ---
    side = side.lower()
    specs = specs.lower()
    if side not in ["right", "left"]:
        raise ValueError("Параметр 'side' должен быть 'right' или 'left'")
    if specs not in ["nhl", "iihf"]:
        raise ValueError("Параметр 'specs' должен быть 'nhl' или 'iihf'")

    # Коэффициент стороны: 1 для правой, -1 для левой, 0 для центральной линии
    side_mult = 1 if side == "right" else -1

    # Разрешение для кругов и дуг
    nsteps = 1001
    circle = np.linspace(0, 2 * np.pi, nsteps)

    # --- Определение параметров (NHL/IIHF) ---
    if specs == "nhl":
        # NHL specifications (All units in feet)
        x_max, y_max = 100, 42.5
        x_blue, x_goal = x_max - 75, x_max - 11
        r_corner = 28
        crease_end, r_crease = 4.5, 6
        net_depth = 40 / 12
        goal_post_start, crease_start_y = 6 / 2, 8 / 2
        crease_smAll_start, crease_smAll_length = 4, 5 / 12
        x_dot_dist, y_faceoff_dot, r_faceoff = 20, 22, 15
        hash_length, hash_space = 2, 67 / 12
        inner_start_x, inner_start_y = 2, 1.5 / 2
        par_side_length, par_end_length = 4, 3
        x_dot_neutral, r_ref = 5, 5  # Ref crease radius is often 10' in NHL, but using 5' as in R code
        y_traps_start, y_traps_end = goal_post_start + 8, 14  # Trapezoid

    elif specs == "iihf":
        # IIHF specifications (All units in meters)
        x_max, y_max = 30, 16
        x_blue, x_goal = x_max - 21.23, x_max - 4
        r_corner = 8.5
        crease_end, r_crease = 1.37, 1.83
        net_depth = 1.12
        goal_post_start, crease_start_y = 1.835 / 2, 2.44 / 2
        crease_smAll_start, crease_smAll_length = 1.22, 0.13
        x_dot_dist, y_faceoff_dot, r_faceoff = 6, 7, 4.5
        hash_length, hash_space = 0.6, 1.7
        inner_start_x, inner_start_y = 0.6, 0.225
        par_side_length, par_end_length = 1.2, 0.9
        x_dot_neutral, r_ref = 1.5, 3

    y_min = -y_max

    # --- Подготовка геометрии ---

    # Углы для округления углов (от 90 до 0 градусов)
    curve_angle = np.linspace(np.pi / 2, 0, nsteps)
    y_curve_end = (y_max - r_corner) + r_corner * np.sin(curve_angle[-1])

    # Углы для полукруга площади ворот
    crease_angles = np.linspace(
        np.pi - np.arccos(crease_end / r_crease),
        np.pi + np.arccos(crease_end / r_crease),
        nsteps
    )

    # Углы для полукруга площади ворот
    # Используем немного больший диапазон, чтобы создать замкнутую фигуру.
    crease_angles_fill = np.linspace(
        np.pi - np.arccos(crease_end / r_crease),
        np.pi + np.arccos(crease_end / r_crease),
        nsteps
    )

    # Координаты дуги
    crease_x = x_goal + r_crease * np.cos(crease_angles_fill)
    crease_y = r_crease * np.sin(crease_angles_fill)

    # Центр дуги (на линии ворот)
    center_crease_x = x_goal * side_mult
    center_crease_y = 0

    # Координата X для точек вбрасывания
    x_faceoff_dot = x_goal - x_dot_dist

    # Угол для хэш-меток
    y_hash = r_faceoff * np.sin(np.arccos((hash_space / 2) / r_faceoff))

    # --- Инициализация графика ---
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 12))

    # Определение границ графика
    x_lim = x_max if side == "right" else x_max * 2
    ax.set_xlim(-0.5 * x_lim, x_lim * side_mult + 0.5 * x_lim)
    ax.set_ylim(y_min - 1, y_max + 1)

    # Установка белого фона и скрытие осей
    ax.set_facecolor("white")
    ax.axis('off')

    # --- Рисование элементов площадки ---

    # Вспомогательная функция для рисования линий
    def draw_line(x1, y1, x2, y2, color='black', linewidth=1, linestyle='solid'):
        ax.plot([x1, x2], [y1, y2], color=color, linewidth=linewidth, linestyle=linestyle)

    # 1. Синяя линия
    draw_line(x_blue * side_mult, y_max, x_blue * side_mult, y_min, color="blue", linewidth=2)

    # 2. Центральная линия (Красная)
    if side == "right":  # Рисуем от центра до края
        draw_line(0, y_max, 0, y_min, color="red", linewidth=2)

        # Центральный dot
        ax.plot(0, 0, 'o', color="blue", markersize=4)

        # Пунктирная/сплошная белая линия поверх красной (NHL/IIHF)
        if specs == "nhl":
            draw_line(0, y_max, 0, y_min, color="white", linewidth=0.5, linestyle='--')
        elif specs == "iihf":
            draw_line(0, 0.5, 0, -0.5, color="white", linewidth=2.5)

        # Центральный круг вбрасывания (только полукруг в правой части)
        center_circle_angles = np.linspace(np.pi / 2, -np.pi / 2, nsteps)
        ax.plot(r_faceoff * np.cos(center_circle_angles) * side_mult,
                r_faceoff * np.sin(center_circle_angles),
                color="blue")

    # 3. Боковые борта
    draw_line(0 * side_mult, y_min, (x_max - r_corner) * side_mult, y_min, linewidth=1)
    draw_line(0 * side_mult, y_max, (x_max - r_corner) * side_mult, y_max, linewidth=1)

    # 4. Угловые скругления
    x_arc = (x_max - r_corner) + r_corner * np.cos(curve_angle)
    y_arc_top = (y_max - r_corner) + r_corner * np.sin(curve_angle)
    y_arc_bottom = -((y_max - r_corner) + r_corner * np.sin(curve_angle))

    ax.plot(x_arc * side_mult, y_arc_top, linewidth=1, color = 'black')
    ax.plot(x_arc * side_mult, y_arc_bottom, linewidth=1, color = 'black')

    # 5. Конечные борта (прямой участок)
    draw_line(x_max * side_mult, y_curve_end, x_max * side_mult, -y_curve_end, linewidth=1)

    # 6. Линия ворот (Красная)
    # y-координата, где линия ворот пересекает скругление
    goal_angle = np.arccos((x_goal - (x_max - r_corner)) / r_corner)
    y_goal = (y_max - r_corner) + r_corner * np.sin(goal_angle)
    draw_line(x_goal * side_mult, y_goal, x_goal * side_mult, -y_goal, color="red")

    # 7. Площадь ворот (Crease) - ЗАЛИВКА

    # 7а. Заливка ПОЛУКРУГЛОЙ ЧАСТИ (Arc/Wedge)
    # Используем patches.Wedge для залитой дуги

    # Центр дуги находится на линии ворот (x_goal)
    center_x_crease = x_goal * side_mult
    center_y_crease = 0

    # Углы для Wedge (в градусах)
    # Начальная точка полукруга (на x_goal - crease_end)
    angle_start = np.degrees(np.pi - np.arccos(crease_end / r_crease))
    # Конечная точка полукруга
    angle_end = np.degrees(np.pi + np.arccos(crease_end / r_crease))

    # # Создаем КЛИН (Wedge)
    # crease_wedge = patches.Wedge(
    #     (center_x_crease, center_y_crease),
    #     r_crease,
    #     angle_start,
    #     angle_end,
    #     facecolor='blue',
    #     edgecolor='none',
    #     zorder=1  # Ниже линий, выше фона
    # )
    # ax.add_patch(crease_wedge)
    #
    # # 7б. Заливка ПРЯМОУГОЛЬНОЙ ЧАСТИ ("Ножки" Crease)
    #
    # # Координаты для прямоугольника (от линии ворот до x_goal - crease_end)
    # x_rect_start = (x_goal - crease_end) * side_mult
    # y_rect_bottom = -crease_start_y
    #
    # width_rect = crease_end
    # height_rect = 2 * crease_start_y
    #
    # # Прямоугольник (x, y - нижний левый угол)
    # rect_crease_fill = patches.Rectangle(
    #     (x_rect_start, y_rect_bottom),
    #     width_rect * side_mult,  # Ширина должна быть положительной/отрицательной в зависимости от side_mult
    #     height_rect,
    #     facecolor='blue',
    #     edgecolor='none',
    #     zorder=1
    # )
    # ax.add_patch(rect_crease_fill)

    # 7в. Рисование КРАСНЫХ контурных линий поверх заливки (ZORDER=2)

    # Полукруг (контур)
    crease_x_plot = x_goal + r_crease * np.cos(crease_angles)
    crease_y_plot = r_crease * np.sin(crease_angles)
    ax.plot(crease_x_plot * side_mult, crease_y_plot, color="red", linewidth=1.5, zorder=2)

    # Боковые линии площади ворот
    draw_line(x_goal * side_mult, crease_start_y, (x_goal - crease_end) * side_mult, crease_start_y, color="red")
    draw_line(x_goal * side_mult, -crease_start_y, (x_goal - crease_end) * side_mult, -crease_start_y, color="red")

    # # Малые внутренние линии
    # for sign in [1, -1]:
    #     draw_line((x_goal - crease_smAll_start) * side_mult, sign * crease_start_y,
    #               (x_goal - crease_smAll_start) * side_mult, sign * (crease_start_y - crease_smAll_length),
    #               color="red")

    # 8. Сетка (Net)
    net_x_end = (x_goal + net_depth) * side_mult
    net_x_goal = x_goal * side_mult
    y_post = goal_post_start

    # Задняя линия
    draw_line(net_x_end, y_post, net_x_end, -y_post)
    # Верхний пост
    draw_line(net_x_goal, y_post, net_x_end, y_post)
    # Нижний пост
    draw_line(net_x_goal, -y_post, net_x_end, -y_post)

    # 9. Точки и круги вбрасывания

    for sign in [1, -1]:
        y_dot = sign * y_faceoff_dot
        x_dot = x_faceoff_dot * side_mult

        # Dot
        ax.plot(x_dot, y_dot, 'o', color="red", markersize=4)

        # Circle
        circle_patch = patches.Circle((x_dot, y_dot), r_faceoff, edgecolor='red', facecolor='none')
        ax.add_patch(circle_patch)

        # 10. Хэш-метки (Hashes)
        hash_x_base = x_faceoff_dot + hash_space / 2
        # print(hash_x_base)
        hash_y_start = y_dot + y_hash
        hash_y_end = y_dot + y_hash + hash_length

        # Хэш 1 (справа от точки, сверху)
        draw_line(side_mult * hash_x_base, hash_y_start, side_mult * hash_x_base, hash_y_end, color="red")
        # Хэш 2 (слева от точки, сверху)
        draw_line(side_mult * hash_x_base - hash_space, hash_y_start, side_mult * hash_x_base - hash_space, hash_y_end, color="red")
        # Хэш 3 (справа от точки, снизу)
        draw_line(side_mult * hash_x_base, -hash_y_start, side_mult * hash_x_base, -(hash_y_end), color="red")
        # Хэш 4 (слева от точки, снизу)
        draw_line(side_mult * hash_x_base - hash_space, -hash_y_start, side_mult * hash_x_base - hash_space, -(hash_y_end), color="red")

        # 11. Внутренние линии (Inner Lines)
        # Параллельные бортам
        for x_sign in [1, -1]:
            for y_sign in [1, -1]:
                x_start = x_faceoff_dot + x_sign * inner_start_x
                x_end = x_faceoff_dot + x_sign * (inner_start_x + par_side_length)
                y_pos = y_dot + y_sign * inner_start_y
                draw_line(side_mult * x_start, y_pos, side_mult * x_end, y_pos, color="red")

                # Параллельные торцевым бортам
                y_start = y_dot + y_sign * inner_start_y
                y_end = y_dot + y_sign * (inner_start_y + par_end_length)
                x_pos = x_faceoff_dot + x_sign * inner_start_x
                draw_line(side_mult * x_pos, y_start, side_mult * x_pos, y_end, color="red")

    # 12. Трапеция (Restricted Area) - Только NHL
    if specs == "nhl":
        y_traps_start_y = y_traps_start
        y_traps_end_y = y_traps_end

        # Линия от линии ворот до борта (вверху)
        draw_line(x_goal * side_mult, y_traps_start_y, x_max * side_mult, y_traps_end_y, color="red")
        # Линия от линии ворот до борта (внизу)
        draw_line(x_goal * side_mult, -y_traps_start_y, x_max * side_mult, -y_traps_end_y, color="red")
        # Линия в конце борта
        draw_line(x_max * side_mult, y_traps_end_y, x_max * side_mult, -y_traps_end_y, color="red")

    # 13. Судейская площадь (Ref Crease)
    # ref_angles = np.linspace(np.pi / 2, 0, nsteps)
    # ref_x = r_ref * np.cos(ref_angles)
    # ref_y = y_min + r_ref * np.sin(ref_angles)
    # ax.plot(ref_x * side_mult, ref_y, color="red")

    # 14. Точки вбрасывания в нейтральной зоне
    if side == "right":
        x_dot_n = (x_blue - x_dot_neutral)
        for sign in [1, -1]:
            ax.plot(x_dot_n, sign * y_faceoff_dot, 'o', color="red", markersize=4)

    ax.set_aspect('equal', adjustable='box')
    # plt.title(f'Хоккейная площадка ({specs.upper()} - {side.capitalize()} Side)', fontsize=14)
    plt.tight_layout()

    if ax.figure is not None:
        return ax.figure, ax
    else:
        return None, ax

df = pd.read_csv(r'static\csv\xg_prediction.csv', index_col=0)
df25 = pd.read_csv(r'static\csv\xg_prediction25.csv', index_col=0)



df = pd.concat([df,df25])
df.reset_index(inplace=True)
df['format'] = df.apply(lambda row: 'PP' if row['format_PP'] == True else 'PK' if row['format_PP'] == True else 'EV', axis=1)
df['pos'] = df.apply(lambda row: 'н' if row['pos_н'] == True else 'з', axis=1)
df['season'] = df['season'].apply(lambda x: str(x)[:4])
df = df[['player_name','game','team','x','y', 'goal', 'team2','stage','home','pos','format','time', 'pred_proba', 'season']]
# print(df.head())
poses = {'нападающие':'н','защитники':'з','All':'All'}
map_types = {'Броски':'shots','Голы':'goals','All':'All'}
def generate_heat_map(season, stage, pos, format, graphic, map_type, team, player, df=df, ax=None, DATA_X_MAX=500, DATA_Y_MAX=500, RINK_X_MAX = 30, RINK_Y_MAX = 32):

    pos = poses[pos]
    map_type=map_types[map_type]
    if player == None or player == 'None':
        player = 'All'
    print(season, stage, pos, format, graphic, map_type, team, player)
    if type(season) != list:
        season = [season]
    # 0. Отбор необходимых данных для формирования тепловых карт из датасета
    # 0.1 На уровне команд
    filename = ''

    if team != 'All':
        filename = team
        df = df[df['team']==team]

    # 0.2 На уровне сезона
    if season != 'All':
        for seasons in season:
            filename += '_'+str(seasons)
        df = df[df['season'].isin(season)]
    # 0.3 На уровне позиции
    if pos != 'All':
        filename += '_' + str(pos)
        df = df[df['pos']==pos]
    # 0.4 На уровне игрока
    if player != 'All':
        filename += '_' + str(player)
        df = df[df['player_name']==player]
    # 0.5 На уровне формата игры All/EV/PP
    if format != 'All':
        filename += '_' + str(format)
        df = df[df['format']==format]

    # 0.6 На уровне этапа плей-офф/регулярный сезон
    # if stage != 'All':
    #     # filename += '_' + str(format)
    #     df = df[df['stage'] == stage]

    # Исходя из типа графики броски или голы
    if map_type != 'shots':
        filename += '_goals_heat_map.png'
        df = df[df['goal']==True]

    else:
        filename += '_shots_heat_map.png'
    # 1. Создание коэффициентов масштабирования
    scale_x = RINK_X_MAX / DATA_X_MAX
    scale_y = RINK_Y_MAX / DATA_Y_MAX

    # 2. Масштабирование исходного DataFrame


    # Масштабирование:
    df_scaled = pd.DataFrame()
    # Масштабируем X (длина) к 0-100.
    df_scaled['x_rink'] = ((500 - df['x']+32)) * scale_x/1.15
    # Масштабируем Y (ширина) к -42.5 до 42.5.
    # Чтобы Y был центрирован вокруг 0, сначала центрируем исходные данные:
    df_scaled['y_rink'] = ((500 - df['y']) - DATA_Y_MAX / 2) * scale_y/1.1

    # Строим схему
    fig, ax = gg_rink(side="right", specs="iihf", ax=ax) # Используем функцию, которую мы разработали
    logos_path = r"static\images\logos"
    max_size = 80  # ограничение по ширине/высоте

    # 2. Строим тепловую карту
    kde = sns.kdeplot(
        data=df_scaled,
        x='x_rink',
        y='y_rink',
        fill=True,  # Заливка области плотности цветом
        cmap="RdPu",  # Выбираем яркую цветовую схему
        thresh=0.08,  # Убираем шум, устанавливая минимальный порог
        levels=10,  # Количество линий уровня (больше линий = более плавный вид),
        ax=ax,  # Обязательно накладываем на оси схемы
        zorder=3,  # Уровень отрисовки (поверх схемы, но ниже аннотаций)
        alpha=0.6,
        cbar=False
    )

    # plt.title(f'Тепловая карта распределения бросков\n сезон - {season}, команда - {team}, позиция - {pos}, игрок - {player}')
    plt.xlabel('Значения y')
    plt.ylabel('Значения x')
    # plt.colorbar()
    # plt.show()
    filepath = r'static\images\heat_map.png'
    # filepath = os.path.join(filepath,filename)
    plt.savefig(filepath, bbox_inches='tight')



def generate_heat_map_points(season, stage, pos, format, graphic, map_type, team, player, df=df, ax=None, DATA_X_MAX=500, DATA_Y_MAX=500, RINK_X_MAX = 30, RINK_Y_MAX = 32):
    if player == None or player == 'None':
        player = 'All'
    print(season, stage, pos, format, graphic, map_type, team, player)
    pos = poses[pos]
    map_type=map_types[map_type]
    if type(season) != list:
        season = [season]
    # 0. Отбор необходимых данных для формирования тепловых карт из датасета
    # 0.1 На уровне команд
    filename = ''

    if team != 'All':
        filename = team
        df = df[df['team']==team]
    # 0.2 На уровне сезона
    if season != 'All':
        for seasons in season:
            filename += '_'+str(seasons)
        df = df[df['season'].isin(season)]
    # 0.3 На уровне позиции
    if pos != 'All':
        filename += '_' + str(pos)
        df = df[df['pos']==pos]
    # 0.4 На уровне игрока
    if player != 'All':
        filename += '_' + str(player)
        df = df[df['player_name']==player]
    # 0.5 На уровне формата игры All/EV/PP
    if format != 'All':
        filename += '_' + str(format)
        df = df[df['format']==format]
    # Исходя из типа графики броски или голы
    if map_type != 'shots':
        filename += '_goals_heat_map.png'
        df = df[df['goal']==True]
    else:
        filename += '_xG_map.png'

    # 1. Создание коэффициентов масштабирования
    scale_x = RINK_X_MAX / DATA_X_MAX
    scale_y = RINK_Y_MAX / DATA_Y_MAX

    # 2. Масштабирование исходного DataFrame


    # Масштабирование:
    df_scaled = pd.DataFrame()
    # Масштабируем X (длина) к 0-100.
    df_scaled['x_rink'] = ((500 - df['x']+32)) * scale_x/1.1

    # Масштабируем Y (ширина) к -42.5 до 42.5.
    # Чтобы Y был центрирован вокруг 0, сначала центрируем исходные данные:
    df_scaled['y_rink'] = ((500 - df['y']) - DATA_Y_MAX / 2) * scale_y/1.0

    df_scaled['xG'] = df['pred_proba']

    # Строим схему
    fig, ax = gg_rink(side="right", specs="iihf", ax=ax) # Используем функцию, которую мы разработали

    # 2. Строим тепловую карту
    plt.scatter(
        x=df_scaled['x_rink'],
        y=df_scaled['y_rink'],
        cmap="coolwarm",  # Выбираем яркую цветовую схему
        vmin=0.0, vmax=0.2,
        c=df_scaled['xG'],
        # ax=ax,
        zorder=3,  # Уровень отрисовки (поверх схемы, но ниже аннотаций)
        alpha=0.6,
    )

    # plt.title(f'Тепловая карта распределения бросков\n сезон - {season}, команда - {team}, позиция - {pos}, игрок - {player}')
    plt.xlabel('Значения y')
    plt.ylabel('Значения x')
    plt.colorbar(shrink=0.3, label = 'xG')
    # plt.show()
    filepath = r'static/images/heat_map.png'
    # filepath = os.path.join(filepath,filename)
    plt.savefig(filepath, bbox_inches='tight')

# generate_heat_map_points('All','All','All')