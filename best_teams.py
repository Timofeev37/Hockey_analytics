import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from matplotlib.patches import Rectangle
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.colors import TwoSlopeNorm, LinearSegmentedColormap
import pandas as pd

columns = {'Команда':'team','Общий рейтинг (Net)':'net','Атакующий рейтинг (Off)':'off','Защитный рейтинг (Def)':'def','Заброшенные шайбы (ЗШ)':'gf','Пропущенный шайбы (ПШ)':'ga','Разница шайб (РШ)':'gd','Ожидаемые шайбы (xG)':'xg','Ожидаемые пропущенные шайбы (xGA)':'xga','Ожидаемая разница шайб (xGD)':'xgd','Шансы на плей-офф':'play-offs'}
order_var = {'По возрастанию':True,'По убыванию':False}

def generate(column, order):
    columns = {'Команда': 'team', 'Общий рейтинг (Net)': 'net', 'Атакующий рейтинг (Off)': 'off',
               'Защитный рейтинг (Def)': 'def', 'Заброшенные шайбы (ЗШ)': 'gf', 'Пропущенный шайбы (ПШ)': 'ga',
               'Разница шайб (РШ)': 'gd', 'Ожидаемые шайбы (xG)': 'xg', 'Ожидаемые пропущенные шайбы (xGA)': 'xga',
               'Ожидаемая разница шайб (xGD)': 'xgd', 'Шансы на плей-офф': 'play-offs'}
    column = columns[column]
    prep_table = pd.read_csv(r'static\csv\best_teams.csv',index_col=0)
    logos_path = r'static\images\logos'
    # Сортируем по net (по аналогии с рейтингом)
    prep_table = prep_table.sort_values(column, ascending=order_var[order]).reset_index(drop=True)

    # === нормализация для цветов ===
    cmap = LinearSegmentedColormap.from_list("blue_white_red", ["#e07a5f", "white", "#8ecae6"])
    norm = TwoSlopeNorm(vmin=prep_table[['off', 'def', 'net']].min().min(),
                        vcenter=prep_table[['off', 'def', 'net']].mean().mean(),
                        vmax=prep_table[['off', 'def', 'net']].max().max())

    # === фигура ===
    fig, ax = plt.subplots(figsize=(12, len(prep_table) * 0.45))
    ax.set_facecolor("#ffffff")
    ax.axis("off")

    row_h = 0.45
    y = 1

    # лимиты для мини-гистограмм
    gf_max = prep_table['gf'].max()
    gf_min = prep_table['gf'].min()
    ga_max = prep_table['ga'].max()
    ga_min = prep_table['ga'].min()
    xg_max = prep_table['xg'].max()
    xg_min = prep_table['xg'].min()
    xga_max = prep_table['xga'].max()
    xga_min = prep_table['xga'].min()
    # ax.axhline(y-0.75, zorder=1, color='black', lw=1)
    ax.plot([-1.5, 12], [y - 0.75, y - 0.75], color='black', lw=1)
    ax.plot([2.85, 12], [y - 0.35, y - 0.35], color='#999999', lw=0.75)
    ax.plot([1.9, 1.9], [y - 0.75, -21.5 * row_h], zorder=11, color='black', lw=0.7)
    ax.plot([2.85, 2.85], [y - 0.75, -21.5 * row_h], zorder=11, color='black', lw=0.7)
    ax.plot([5.9, 5.9], [y - 0.75, -21.5 * row_h], zorder=11, color='black', lw=0.7)
    ax.plot([9.49, 9.49], [y - 0.75, -21.5 * row_h], zorder=11, color='black', lw=0.7)
    ax.plot([12.55, 12.55], [y - 0.75, -21.5 * row_h], zorder=11, color='black', lw=0.7)
    # === отрисовка ===
    for i, row in prep_table.iterrows():
        y = -i * row_h
        ax.axhline(y - row_h / 2, zorder=1, color='#f7f7f7', lw=0.75)

        # чередующийся фон
        # if i % 2 == 0:
        #     ax.add_patch(Rectangle((-0.2, y - row_h / 2), 12.3, row_h,
        #                            facecolor="#fafafa", edgecolor="none"))
        max_size = 80  # ограничение по ширине/высоте
        logo_path = os.path.join(logos_path, f"{row['team_name_long']}.png")
        if os.path.exists(logo_path):
            logo_img = mpimg.imread(logo_path)

            # Определяем реальный размер изображения
            h, w = logo_img.shape[:2]

            # Вычисляем коэффициент масштабирования
            scale = min(max_size / w, max_size / h)

            # OffsetImage работает с "zoom", а не пикселями
            # Подбираем zoom как отношение к 1.0 (на глаз подгоняется под DPI matplotlib)
            zoom = scale / 4

            imagebox = OffsetImage(logo_img, zoom=zoom)
            imagebox.image.axes = ax

            ab = AnnotationBbox(
                imagebox,
                (-.74, y),  # позиция
                xycoords='data',
                frameon=False,
                zorder=9
                # box_alignment=(1, 0.5)
            )

            ax.add_artist(ab)

        # Команда
        ax.text(-0.51, y, f"{row['team']}",
                ha='left', va='center', fontsize=10, color="black")
        ax.text(-0.51, y, " " * (2 * len(row['team']) + 4) + f"{row['record']}",
                ha='left', va='center', fontsize=9, color="#222", alpha=0.8)

        # Плей-офф
        ax.text(2.375, y,
                f"{int(row['play-offs']) if row['play-offs'] >= 1 else '>0' if row['play-offs'] > 0 else '>0'}%",
                ha='center', va='center', fontsize=10, color="#444", alpha=0.5 + 0.5 * row['play-offs'] / 100)

        # Шайбы — симметричная мини-гистограмма
        base_x = 2.95
        base_x1 = 4.25
        gf_width = (row['gf'] / gf_max * 0.9) ** 1.8
        ga_width = ((1 + ga_min / (ga_max) - (row['ga'] / ga_max)) * 0.9) ** 1.8
        ax.barh(y, 0.9 ** 1.8, height=0.1, color="#E1E1E1", left=base_x)
        ax.barh(y, gf_width, height=0.1, color="#219ebc", left=base_x)

        ax.barh(y, 0.9 ** 1.8, height=0.1, color="#E1E1E1", left=base_x1)
        ax.barh(y, ga_width, height=0.1, color="#8ecae6", left=base_x1)

        ax.text(base_x + 0.9, y, f"{int(row['gf'])}",
                ha='left', va='center', fontsize=9, color="#333")
        ax.text(base_x1 + 0.9, y, f"{int(row['ga'])}",
                ha='left', va='center', fontsize=9, color="#333")
        if row['gd'] > 0:
            color = 'green'
            text = f"+{int(row['gd'])}"
        elif row['gd'] < 0:
            color = 'red'
            text = f"{int(row['gd'])}"
        else:
            color = 'black'
            text = f"{int(row['gd'])}"
        ax.text(base_x1 + 1.25, y, text,
                ha='left', va='center', fontsize=9, color=color)
        # xG — симметрично, красноватые оттенки
        base_x = 5.95
        base_x1 = 7.4
        xg_width = (row['xg'] / xg_max * 0.9) ** 1.8
        xga_width = ((1 + xga_min / xga_max - row['xga'] / xga_max) * 0.9) ** 1.8
        ax.barh(y, 0.9 ** 1.8, height=0.1, color="#E1E1E1", left=base_x)
        ax.barh(y, xg_width, height=0.1, color="#99582a", left=base_x)
        ax.barh(y, 0.9 ** 1.8, height=0.1, color="#E1E1E1", left=base_x1)
        ax.barh(y, xga_width, height=0.1, color="#e07a5f", left=base_x1)

        ax.text(base_x + 0.9, y, f"{row['xg']:.1f}",
                ha='left', va='center', fontsize=9, color="#333")
        ax.text(base_x1 + 0.9, y, f"{row['xga']:.1f}",
                ha='left', va='center', fontsize=9, color="#333")
        if row['xgd'] > 0:
            color = 'green'
            text = f"+{row['xgd']:.1f}"
        elif row['xgd'] < 0:
            color = 'red'
            text = f"{row['xgd']:.1f}"
        else:
            color = 'black'
            text = f"{row['xgd']:.1f}"
        ax.text(base_x1 + 1.5, y, text,
                ha='left', va='center', fontsize=9, color=color)
        # Блок рейтингов: три прямоугольника (Off / Def / Net)
        start_x = 9.55
        w = 0.8
        for j, col in enumerate(['off', 'def', 'net']):
            val = row[col]
            color = cmap(norm(val))
            ax.add_patch(Rectangle((start_x + j * w, y - 0.16), w - 0.05, 0.32,
                                   facecolor=color, edgecolor='lightgray', lw=0.5))
            ax.text(start_x + j * w + (w - 0.05) / 2, y, f"{val:.1f}",
                    ha='center', va='center', fontsize=10, color="#111")

    # === заголовки ===
    ax.text(-0.9, 0.4, "Команда", ha='left', fontsize=10, weight='bold', color="#111")
    ax.text(2.375, 0.4, "Плей-офф", ha='center', fontsize=10, weight='bold', color="#111")
    ax.text(4.4, 0.75, "Шайбы", ha='center', fontsize=10, weight='bold', color="#111")
    ax.text(7.54, 0.75, "Показатели xG", ha='center', fontsize=10, weight='bold', color="#111")
    ax.text(10.62, 0.75, "Рейтинг", ha='center', fontsize=10, weight='bold', color="#111")
    ax.text(3.35, 0.4, "ЗШ", ha='center', fontsize=10, color="#111")
    ax.text(4.65, 0.4, "ПШ", ha='center', fontsize=10, color="#111")
    ax.text(5.6, 0.4, "РШ", ha='center', fontsize=10, color="#111")
    ax.text(6.45, 0.4, "xG", ha='center', fontsize=10, color="#111")
    ax.text(7.85, 0.4, "xGA", ha='center', fontsize=10, color="#111")
    ax.text(9.07, 0.4, "xGD", ha='center', fontsize=10, color="#111")

    # ax.text(-0.9, 1.35, "КХЛ 2025/26 Командные рейтинги и статистика", weight='bold', ha='left', fontsize=16,
    #         color="#111")
    # ax.text(11.9, 1.45, "t.me/ice_forecast", ha='right', fontsize=10, color="#111", alpha=0.75)

    # подписи над прямоугольниками рейтинга
    rating_labels = ['Off', 'Def', 'Net']
    for j, lbl in enumerate(rating_labels):
        ax.text(9.55 + j * 0.8 + 0.35, 0.4, lbl, ha='center', fontsize=10, color="#111")

    ax.set_xlim(-0.9, 11.9)
    ax.set_ylim(-len(prep_table) * row_h, 0.8)
    # plt.tight_layout()
    # plt.show()
    name = f'best_teams.png'
    filepath = r'static\images'
    filename = os.path.join(filepath, name)
    plt.savefig(filename, dpi=300, bbox_inches='tight')