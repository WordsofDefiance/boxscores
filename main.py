from basketball_reference_web_scraper import client
from basketball_reference_web_scraper.data import Team
from basketball_reference_web_scraper.data import OutputType
import json
from datetime import date

def boxScoreToReddit(box_score):
    name = box_score['name']
    minutes = box_score['seconds_played'] // 60
    seconds = box_score['seconds_played'] % 60
    time_played = '{}:{}'.format(minutes, str(seconds).zfill(2))
    if box_score['made_field_goals'] != 0:
        field_goal_percentage = box_score['made_field_goals'] / box_score['attempted_field_goals'] * 100
    else: 
        field_goal_percentage = 0
    field_goals = '{}-{} ({}%)'.format( str(box_score['made_field_goals']), str(box_score['attempted_field_goals']), str(round(field_goal_percentage, 2)))
    if box_score['attempted_three_point_field_goals'] != 0:
        threes_percentage = box_score['made_three_point_field_goals'] / box_score['attempted_three_point_field_goals'] * 100
    else:
        threes_percentage = 0
    threes = '{}-{} ({}%)'.format(str(box_score['made_three_point_field_goals']), str(box_score['attempted_three_point_field_goals']), str(round(threes_percentage, 2)))
    if box_score['attempted_free_throws'] != 0:
        free_throws_percentage = box_score['made_free_throws'] / box_score['attempted_free_throws'] * 100
    else: 
        free_throws_percentage = 0
    free_throws = '{}-{} ({}%)'.format( str(box_score['made_free_throws']),str(box_score['attempted_free_throws']), str(round(free_throws_percentage, 2)))
    offensive_rebounds = box_score['offensive_rebounds']
    total_rebounds = getTotalRebounds(box_score)
    assists = box_score['assists']
    steals = box_score['steals']
    blocks = box_score['blocks']
    turnovers = box_score['turnovers']
    personal_fouls = box_score['personal_fouls']
    points = getPoints(box_score)
    game_score = box_score['game_score']

    data = '{} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} |'.format(name, time_played, field_goals, threes, free_throws, offensive_rebounds, total_rebounds, assists, turnovers, steals, blocks, personal_fouls, points, game_score)
    data+= "\n"
    return data

def teamTotalsToReddit(day, month, year, team):
    team_totals = client.team_box_scores(day=day, month=month, year=year)
    for score in team_totals:
        if score['team'] == team:
            attempted_field_goals = '{}-{} ({}%)'.format( score['made_field_goals'], 
                score['attempted_field_goals'], 
                str(round(score['made_field_goals'] / score['attempted_field_goals'] * 100, 2))
                )
            attempted_threes = '{}-{} ({}%)'.format( score['made_three_point_field_goals'], 
                score['attempted_three_point_field_goals'], 
                str(round(score['made_three_point_field_goals'] / score['attempted_three_point_field_goals'] * 100, 2))
                )
            free_throws = '{}-{} ({}%)'.format( score['made_free_throws'], 
                score['attempted_free_throws'], 
                str(round(score['made_free_throws'] / score['attempted_free_throws'] * 100, 2))
                )
            points = score['made_free_throws'] + (( score['made_field_goals'] - score['made_three_point_field_goals'] ) * 2) + (score['made_three_point_field_goals'] * 3)
            data = 'TOTALS: | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | --- |'.format(
                score['minutes_played'],
                attempted_field_goals, 
                attempted_threes, 
                free_throws, 
                score['offensive_rebounds'], 
                score['offensive_rebounds'] + score['defensive_rebounds'], 
                score['assists'], 
                score['turnovers'], 
                score['steals'], 
                score['blocks'], 
                score['personal_fouls'], 
                points)
            data += "\n"
    return data

def getPoints(box_score):
    return box_score['made_free_throws'] + (box_score['made_three_point_field_goals'] * 3) + ( (box_score['made_field_goals'] - box_score['made_three_point_field_goals']) * 2)

def getTotalRebounds(box_score):
    return box_score['offensive_rebounds'] + box_score['defensive_rebounds']

def getTeamDict(enum):
    teamDict = {}
    for i, team in enumerate(enum):
        teamDict[i] = team
    return teamDict



"""
MAIN 
"""
teams = getTeamDict(Team)

for i, team in enumerate(teams):
    uppercaseTeam = teams[i].name.replace('_', ' ').lower().title()

    print("{0:10}:    {1} \n".format(i, uppercaseTeam))

while True:
    try:
        team = input("What team are you looking for? ")
        team = int(team)
        if team > len(teams) - 1 or team < 0:
            raise ValueError
        year = int(input("What year? \n"))
        if year < 1990 or year > date.today().year:
            raise ValueError
        month = int(input("What month? \n"))
        if month < 1 or month > 12:
            raise ValueError
        day = int(input("What day? \n"))
        if day < 1 or day > 31:
            raise ValueError
    except ValueError as err:
        if ("invalid literal" in str(err)):
            print("\nIntegers only, please. Try Again.\n")
        elif team > len(teams) -1 or team < 0:
            print("Your value must be between 0 and {}".format(len(teams)))
        elif year < 1990 or year > date.today().year:
            print("You must select a year between 1991 and {}".format(date.today().year))
        elif month < 1 or month > 12:
            print("You must select a valid month")
        elif day < 1 or day > 31:
            print('You must select a valid day \(between 1 and 31\)')
    else:
        print("You selected {} on {}-{}-{}".format(teams[team].name, year, month, day))
        break
    finally:
        # For the Selected Team:
        box_scores = client.player_box_scores(day=day, month=month, year=year)
        if box_scores != []:
            team = teams[team]
            headers= '{}|Min|FG|3PT|FT|OR|Reb|Ast|TO|Stl|Blk|PF|Pts|Game Score'.format(team.name[0:3])
            align  = ':--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--'
            data  = ''
            opponent = ''

            # Get the Selected Team's totals
            for box_score in box_scores:
                if box_score['team'] == team:
                    # Add the
                    data += boxScoreToReddit(box_score)

            data += teamTotalsToReddit(day, month, year, team)

            print(headers)
            print(align)
            print(data)

            # For the Opposing Team:
            for box_score in box_scores:
                if box_score['team'] == team:
                    opponent = box_score['opponent']
                    break
            headers= '{}|Min|FG|3PT|FT|OR|Reb|Ast|TO|Stl|Blk|PF|Pts|Game Score'.format(opponent.name[0:3])
            align  = ':--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--'
            data  = ''

            for box_score in box_scores:
                if box_score['team'] == opponent:
                    data += boxScoreToReddit(box_score)

            data += teamTotalsToReddit(day, month, year, opponent)

            print(headers)
            print(align)
            print(data)
        else:
            print('No game found for {} on {}-{}-{}'.format(teams[team].name, year, month, day))
 

