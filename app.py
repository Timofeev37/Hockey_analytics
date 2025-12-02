from flask import Flask, render_template, request
import best_players
import best_teams
import shots_map

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

#для странички best_teams
COLUMNS = ['Команда','Общий рейтинг (Net)','Атакующий рейтинг (Off)','Защитный рейтинг (Def)','Заброшенные шайбы (ЗШ)','Пропущенный шайбы (ПШ)','Разница шайб (РШ)','Ожидаемые шайбы (xG)','Ожидаемые пропущенные шайбы (xGA)','Ожидаемая разница шайб (xGD)','Шансы на плей-офф']
ORDER_VAR = ['По возрастанию','По убыванию']
#для странички best_goalies
ORDER_VAR_G = ['10 лучших вратарей по GSAx','10 худших вратарей по GSAx']
#для странички shot_map
SEASON_VAR = ['2024','2025','2026','All']
STAGE_VAR = ['regular season', 'All']
POS_VAR = ['нападающие','защитники','All']
FORMAT_VAR = ['EV','PP','PK','All']
GRAPHIC_VAR = ['Тепловая карта','Точечное распределение']
MAP_TYPE_VAR_POINTS = ['Броски','Голы','xG']
MAP_TYPE_VAR_HEAT = ['Броски','Голы']
TEAM_VAR = ['All', 'Авангард', 'Автомобилист', 'Адмирал', 'Ак Барс', 'Амур', 'Барыс', 'Динамо М', 'Динамо Мн', 'Лада', 'Локомотив', 'Металлург', 'Нефтехимик', 'Салават Юлаев', 'Северсталь', 'Сибирь', 'Трактор', 'ЦСКА', 'Шанхайские Драконы', 'СКА', 'Спартак', 'Торпедо', 'ХК Сочи']




@app.route('/teams', methods=['GET', 'POST'])
def teams():
    col = None
    order = None
    if request.method == 'POST':
        col = request.form['column']
        order = request.form['order']
        best_teams.generate(col, order)
        return render_template('best_teams.html',
                               columns=COLUMNS,
                               order_var = ORDER_VAR,
                               image_ready=True)

    return render_template('best_teams.html',
                           columns=COLUMNS,
                           order_var=ORDER_VAR,
                           selected_col=col,
                           selected_order=order,
                           image_ready=(col is not None))

@app.route('/players', methods=['GET', 'POST'])
def players():
    order = None
    if request.method == 'POST':
        order = request.form['order']
        best_players.generate(order)
        return render_template('best_players.html',
                               order_var = ORDER_VAR_G,
                               image_ready=True)

    return render_template('best_players.html',
                           order_var=ORDER_VAR_G,
                           selected_order=order,
                           image_ready=(order is not None))

@app.route('/shots', methods=['GET', 'POST'])
def shots():
    filters = {
        "season": None,
        "stage": None,
        "pos": None,
        "format": None,
        "graphic": None,
        "map_type": None,
        "team": None,
        "player": None
    }

    if request.method == 'POST':
        filters["season"] = request.form.get("season")
        filters["stage"] = request.form.get("stage")
        filters["pos"] = request.form.get("pos")
        filters["format"] = request.form.get("format")
        filters["graphic"] = request.form.get("graphic")
        filters["map_type"] = request.form.get("map_type")
        filters["team"] = request.form.get("team")
        filters["player"] = request.form.get("player")

        # выбор набора типов карты
        if filters["graphic"] == "Тепловая карта":
            valid_maps = MAP_TYPE_VAR_HEAT
        else:
            valid_maps = MAP_TYPE_VAR_POINTS

        # выбор функции
        if filters["graphic"] == 'Тепловая карта':
            shots_map.generate_heat_map(**filters)
        else:
            shots_map.generate_heat_map_points(**filters)

        return render_template(
            "shots_map.html",
            season_list=SEASON_VAR,
            stage_list=STAGE_VAR,
            pos_list=POS_VAR,
            format_list=FORMAT_VAR,
            graphic_list=GRAPHIC_VAR,
            map_type_list=valid_maps,
            team_list=TEAM_VAR,
            selected=filters,
            image_ready=True
        )

    return render_template(
        "shots_map.html",
        season_list=SEASON_VAR,
        stage_list=STAGE_VAR,
        pos_list=POS_VAR,
        format_list=FORMAT_VAR,
        graphic_list=GRAPHIC_VAR,
        map_type_list=MAP_TYPE_VAR_HEAT,   # по умолчанию
        team_list=TEAM_VAR,
        selected=filters,
        image_ready=False
    )

if __name__ == "__main__":
    app.run(debug=True)