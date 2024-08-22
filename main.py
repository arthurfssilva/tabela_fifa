import flet as ft
from datetime import datetime

# Função para verificar e criar os arquivos necessários
def check_and_create_files():
    try:
        with open("teams.txt", "x") as f:
            f.write("TeamA,0,0,0,0,0,0,0,0\n")
            f.write("TeamB,0,0,0,0,0,0,0,0\n")
    except FileExistsError:
        pass

    try:
        with open("matchhistory.txt", "x") as f:
            pass
    except FileExistsError:
        pass

def main(page: ft.Page):
    # Verificar e criar os arquivos antes de qualquer operação
    check_and_create_files()
    
    page.title = "UEFA Chapados League"
    
    # Função para adicionar uma partida ao histórico
    def add_match_to_history(team1, team2, goals1, goals2):
        match_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("matchhistory.txt", "a") as f:
            f.write(f"{match_date},{team1},{goals1},{team2},{goals2}\n")

    # Função para exibir o histórico de partidas
    def view_match_history():
        with open("matchhistory.txt", "r") as f:
            matches = [line.strip().split(",") for line in f.readlines()]

        matches.sort(key=lambda x: datetime.strptime(x[0], "%Y-%m-%d %H:%M:%S"), reverse=True)
        
        match_history_list.controls.clear()
        for match in matches:
            match_date, team1, goals1, team2, goals2 = match
            match_history_list.controls.append(ft.Text(f"{match_date} - {team1} {goals1} x {goals2} {team2}"))
        page.update()

    # Função para a página de gerenciamento de times
    def manage_teams_page(page):
        # Função para adicionar um novo time
        def add_team(e):
            team_name = new_team_name.value
            if team_name:
                with open("teams.txt", "a") as f:
                    f.write(f"{team_name},0,0,0,0,0,0,0,0\n")
                new_team_name.value = ""
                page.snack_bar = ft.SnackBar(ft.Text("Time adicionado com sucesso!"))
                page.snack_bar.open = True
                page.update()
        
        # Função para apagar todos os dados
        def delete_all_data(e):
            with open("teams.txt", "w") as f:
                f.write("")
            page.snack_bar = ft.SnackBar(ft.Text("Todos os dados foram apagados!"))
            page.snack_bar.open = True
            page.update()
        
        new_team_name = ft.TextField(label="Nome do Novo Time")
        add_team_button = ft.ElevatedButton(text="Adicionar Time", on_click=add_team)
        delete_all_button = ft.ElevatedButton(text="Apagar Todos os Dados", on_click=delete_all_data)
        
        return ft.View(
            "/manage_teams",
            [
                ft.AppBar(title=ft.Text("Gerenciar Times"), bgcolor=ft.colors.SURFACE_VARIANT, leading=ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: page.go("/"))),
                new_team_name,
                add_team_button,
                delete_all_button
            ]
        )
       
    # Função para a página da tabela
    def table_page(page):
        # Função para atualizar a visualização da tabela
        def update_table_view():
            with open("teams.txt", "r") as f:
                teams = [line.strip().split(",") for line in f.readlines()]
            
            # Ordenar as equipes de acordo com as regras de desempate
            teams.sort(key=lambda x: (int(x[1]), int(x[3]), int(x[8]), int(x[6])), reverse=True)
            
            table.rows.clear()
            for team in teams:
                table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(team[0])),
                            ft.DataCell(ft.Text(team[1])),
                            ft.DataCell(ft.Text(team[2])),
                            ft.DataCell(ft.Text(team[3])),
                            ft.DataCell(ft.Text(team[4])),
                            ft.DataCell(ft.Text(team[5])),
                            ft.DataCell(ft.Text(team[6])),
                            ft.DataCell(ft.Text(team[7])),
                            ft.DataCell(ft.Text(team[8]))
                        ]
                    )
                )
            page.update()
        
        # Configuração da tabela
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nome")),
                ft.DataColumn(ft.Text("Pontos")),
                ft.DataColumn(ft.Text("Jogos")),
                ft.DataColumn(ft.Text("Vitórias")),
                ft.DataColumn(ft.Text("Empates")),
                ft.DataColumn(ft.Text("Derrotas")),
                ft.DataColumn(ft.Text("Gols Feitos")),
                ft.DataColumn(ft.Text("Gols Sofridos")),
                ft.DataColumn(ft.Text("Saldo de Gols"))
            ],
            rows=[]
        )
        
        update_table_view()
        
        return ft.View(
            "/table",
            [
                ft.AppBar(title=ft.Text("Tabela de Pontuação"), bgcolor=ft.colors.SURFACE_VARIANT, leading=ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: page.go("/"))),
                table
            ]
        )
    
    # Função para a página de cadastro de partidas
    def matches_page(page):
        # Função para adicionar uma partida
        def add_match(e):
            t1 = team1.value
            t2 = team2.value
            g1 = int(team1_goals.value)
            g2 = int(team2_goals.value)
            update_scores(t1, t2, g1, g2)
            add_match_to_history(t1, t2, g1, g2)
            team1.value = ""
            team2.value = ""
            team1_goals.value = ""
            team2_goals.value = ""
            page.go("/table")  # Atualizar a tabela ao adicionar um jogo
        
        # Função para atualizar a pontuação das equipes
        def update_scores(team1, team2, goals1, goals2):
            with open("teams.txt", "r") as f:
                teams = [line.strip().split(",") for line in f.readlines()]
            
            for team in teams:
                if team[0] == team1:
                    update_team(team, goals1, goals2)
                if team[0] == team2:
                    update_team(team, goals2, goals1)
            
            with open("teams.txt", "w") as f:
                for team in teams:
                    f.write(",".join(map(str, team)) + "\n")
        
        # Função para atualizar os dados de uma equipe
        def update_team(team, goals_for, goals_against):
            team[2] = int(team[2]) + 1
            team[6] = int(team[6]) + goals_for
            team[7] = int(team[7]) + goals_against
            team[8] = int(team[6]) - int(team[7])
            
            if goals_for > goals_against:
                team[1] = int(team[1]) + 3
                team[3] = int(team[3]) + 1
            elif goals_for == goals_against:
                team[1] = int(team[1]) + 1
                team[4] = int(team[4]) + 1
            else:
                team[5] = int(team[5]) + 1
        
        # Elementos da página de cadastro de partidas
        team1 = ft.TextField(label="Equipe 1")
        team2 = ft.TextField(label="Equipe 2")
        team1_goals = ft.TextField(label="Gols Equipe 1")
        team2_goals = ft.TextField(label="Gols Equipe 2")
        add_match_button = ft.ElevatedButton(text="Adicionar Partida", on_click=add_match)
        
        return ft.View(
            "/matches",
            [
                ft.AppBar(title=ft.Text("Cadastro de Partidas"), bgcolor=ft.colors.SURFACE_VARIANT, leading=ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: page.go("/"))),
                team1,
                team2,
                team1_goals,
                team2_goals,
                add_match_button
            ]
        )

    # Função para a página de histórico de partidas
    def match_history_page(page):
        return ft.View(
            "/match_history",
            [
                ft.AppBar(title=ft.Text("Histórico de Partidas"), bgcolor=ft.colors.SURFACE_VARIANT, leading=ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: page.go("/"))),
                match_history_list
            ]
        )
    
    # Roteamento
    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(
                ft.View(
                    "/",
                    [
                        ft.AppBar(title=ft.Text("UEFA Chapados League"), bgcolor=ft.colors.SURFACE_VARIANT),
                        ft.ListView(
                            [
                                ft.ElevatedButton("Tabela", on_click=lambda _: page.go("/table")),
                                ft.ElevatedButton("Partidas", on_click=lambda _: page.go("/matches")),
                                ft.ElevatedButton("Criar Time", on_click=lambda _: page.go("/manage_teams")),
                                ft.ElevatedButton("Histórico de Partidas", on_click=lambda _: page.go("/match_history")),
                            ]
                        )
                    ]
                )
            )
        elif page.route == "/table":
            page.views.append(table_page(page))
        elif page.route == "/matches":
            page.views.append(matches_page(page))
        elif page.route == "/manage_teams":
            page.views.append(manage_teams_page(page))
        elif page.route == "/match_history":
            view_match_history()
            page.views.append(match_history_page(page))
        page.update()
    
    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)
    
    # Inicializar a lista de histórico de partidas
    match_history_list = ft.ListView(controls=[])

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    page.go(page.route)

ft.app(target=main)
