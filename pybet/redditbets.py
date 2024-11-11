import json
import locale
from datetime import datetime
import pytz

max_points = 1000
username = 'Critical_Tea_Pot'
locale.setlocale(locale.LC_ALL, 'de_DE')

dateformat = '%Y-%m-%d %H:%M'
timezone = pytz.timezone('Europe/Berlin')

def get_now():
    return datetime.now(timezone)

def get_due_datetime(bet):
    return datetime.strptime(bet['due'], dateformat).replace(tzinfo=timezone)
    
def is_open(bet):
    return get_now() < get_due_datetime(bet)

def get_totals(bet):
    total = {}
    for command in bet['options']:
        total[command] = bet['options'][command]['basePoints']

    for stakes_key in bet['stakes'].keys():
        stake = bet['stakes'][stakes_key]
        total[stake['option']] += stake['points']
    return total

def get_ratio(key, totals):
    return sum(totals.values()) / totals[key]

def round_de(number, digits):
    format = '%.' + str(digits) + 'f'
    return locale.format_string(format, number, 1)

def format_de(number):
    return locale.format_string("%g", number, 1)


def get_post_text(bet):
    body = bet['description']
    body += "\n\n"

    body += "# Aktuell Status\n"

    result = None
    if 'result' in bet.keys():
        result = bet['result']
        option = bet['options'][result]
        body += "**Finales Ergebnis: \"%s\" - \"%s\"**\n\n" % (result, option['title']  )
        body += "Gewinn und Verlust stehen in der Liste unten. Aktuellen Punktestand über alle Wetten findet ihr [hier](https://www.reddit.com/r/mauerstrassenwetten/comments/1ggb43d/mswetten_aktueller_punktestand/)"
    elif is_open(bet):
        body += f"Wetten offen bis {bet['due']} \n"
    else:
        body += "**Wette geschlossen! Es werden keine neuen Wetten angenommen!**\n"
    # body += "\n\nMehr Details in [diesem Thread](https://www.reddit.com/user/Critical_Tea_Pot/comments/1g8dsu0/faq_regelwerk_f%C3%BCr_wetten/)"
    body += "\n"
    total = get_totals(bet)
    print(total)
    
    total_points = sum(total.values())

    if is_open(bet):
        body += "## Aktuelle Quoten\n"
    else:
        body += "## Finale Quoten\n"
    body += "|Befehl|Beschreibung|Punkte|Anteil|Quote|\n"
    body += "|:-----|:-----------|:-----|:-----|:----|\n"
    for command in total.keys():
        ratio = total[command]/total_points
        description = bet['options'][command]['title']
        body += f"|**{command}**|{description}|{total[command]}|{round_de(100*ratio,1)}%| **1 : {round_de(get_ratio(command, total),1)}**|\n"

    body += "\n"
    body += f"## Registrierte Wetten ({len(bet['stakes'].keys())})\n"
    if result is not None:
        body += "|Nutzer|Befehl|Punkte|Quote|Gewinn/Verlust|\n"
        body += "|:-----|:-----|:-----|:----|:-------------|\n"
        for stake_key in bet['stakes'].keys():
            stake = bet['stakes'][stake_key]
            ff = "**" if stake['option'] == result else "~~"
            body += f"|{ff}{stake['user']}{ff}| {ff}{stake['option']}{ff} | {ff}{stake['points']}{ff} | {ff}{format_de(stake['ratio'])}{ff} | {ff}{format_de(stake['winloss'])}{ff}\n"
            # if stake['option'] == result:
                #body += f"|**{stake['user']}**| **{stake['option']}** | **{stake['points']}** | **{format_de(stake['ratio'])}** | **{format_de(stake['winloss'])}**\n"
            #else:
                #body += f"|{stake['user']} | ~~{stake['option']}~~ | ~~{stake['points']}~~ | {format_de(stake['ratio'])} | {format_de(stake['winloss'])}\n"
    else:
        body += "|Nutzer|Befehl|Punkte|Quote|\n"
        body += "|:-----|:-----|:-----|:----|\n"
        for stake_key in bet['stakes'].keys():
            stake = bet['stakes'][stake_key]
            body += f"|{stake['user']} | {stake['option']} | {stake['points']} | {format_de(stake['ratio'])} |\n"

    print(body)
    return body.strip()

def save_bets_to_file(bets, json_path):
    with open(json_path, 'w') as f:
        return json.dump(bets, f, indent=4)

def load_bets_from_file(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

def confirm_stake(comment, message):
    print(message)
    stake_confirmed = False
    for reply in comment.replies:
        if reply.author.name != username:
            continue
        stake_confirmed = True
        # reply.edit(message)
    if not stake_confirmed:
        comment.reply(message)

def get_points_remaining(user, bet):
    points = max_points
    for stake in bet['stakes'].values():
        if user == stake['user']:
            points -= stake['points']
    return points

def get_command(comment, bet):
    input_command = comment.strip("*")
    #in_markdown = False
    #for c in list(comment):
        #if not in_markdown and c == '[':
            #in_markdown = True
        #elif in_markdown and c == ']':
            #in_markdown = False
        #elif not in_markdown:
            #input_command += c
    print("%s -> %s" % (comment, input_command))
    for command in bet['options'].keys():
        if command.lower() == input_command.lower():
            return command
    return None

def process_comment(comment, bet, totals):
    body_parts = comment.body.strip().replace("\n", " ").replace("\t", " ").split(" ", 2)
    command = body_parts[0]

    command = get_command(body_parts[0], bet)
    if command == None:
        print(f"Skip comment (no command found for '{command}'): {comment.id} {comment.author.name}: {comment.created_utc}, Subcomments: {len(comment.replies)}: {body_parts}")
        return False

    try:
        points = int(body_parts[1])
    except:
        confirm_stake(comment, f"Wette wurde nicht registriert, weil die Punktzahl nicht gelesen werden konnte: {body_parts}")
        return False

    available_points = get_points_remaining(comment.author.name, bet)
    if points > available_points:
        confirm_stake(comment, f"Wette wurde nicht registriert, weil nicht ausreichend Punkte verfügbar sind. Verfügbare Punkte aktuell: {available_points}")
        return False

    if points < 0:
        confirm_stake(comment, "Wette wurde nicht registriert, weil keine negativen Punkte gesetzt werden können!")
        return False

    option = bet['options'][command]
    print(f"{comment.author.name} puts {points} on {option['title']}")
    ratio = round(get_ratio(command, totals), 1)
    bet["stakes"][comment.id] = { "user": comment.author.name, "option": command, "points" : points, "ratio": ratio }
    message = f"Wette registriert: {comment.author.name} wettet {points} Punkte auf \"{option['title']}\" mit Quote 1 : {format_de(ratio)}. Bei Gewinn werden +{format_de(points*(ratio-1))} Punkte ausgezahlt ({format_de(points*ratio)} Gewinn - {points} Einsatz)"
    confirm_stake(comment, message)

    return True

def process_winloss(bet):
    result = bet['result']
    for stakes_key in bet['stakes'].keys():
        stake = bet['stakes'][stakes_key]
        if stake['option'] == result:
            stake['winloss'] = stake['points']*(stake['ratio']-1)
        else:
            stake['winloss'] = -1*stake['points']

def update_scoreboard(reddit, bets):
    scores = {}
    for bet in bets['bets']:
        for stake_key in bet['stakes'].keys():
            stake = bet['stakes'][stake_key]
            if 'winloss' in stake.keys():
                if stake['user'] not in scores.keys():
                    scores[stake['user']] = 0
                scores[stake['user']] += stake['winloss']
    scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)

    body = ""
    body += "Hier findet ihr den aktuellen Punktestand von MSWetten. Aktuell noch laufende Wetten werden nicht berücksichtigt.\n\n"
    body += "|#|Nutzer |Punktestand|\n"
    body += "|--:|:--|:--|\n"
    position = 1
    for score in scores:
        body += f"| {position}. | {score[0]} | {format_de(score[1])}|\n"
        position += 1

    submission = reddit.submission(bets['scoreboard'])
    submission.edit(body)


def process_bets(reddit, json_path):
    bets = load_bets_from_file(json_path)

    for bet in bets['bets']:
        process_bet(reddit, bet)
        save_bets_to_file(bets, json_path)
    
    update_scoreboard(reddit, bets)
    save_bets_to_file(bets, json_path)

def process_bet(reddit, bet):
    changed = False
    submission = reddit.submission(bet['id'])

    print(f"Open: {is_open(bet)}, expiration {bet['due']}, remaining: {get_due_datetime(bet)-get_now()}")

    if "result" in bet.keys():
        process_winloss(bet)


    if is_open(bet):

        submission.comments.replace_more(limit=0)
        comments = list(submission.comments)
        comments.sort( key = lambda c: c.created_utc)
        totals = get_totals(bet)
    
        for comment in submission.comments:
            if comment.id in bet["stakes"].keys():
                # print(f"Skip comment (already processed): {comment.id} {comment.author.name}: {comment.created_utc}, Subcomments: {len(comment.replies)}")
                continue

            if comment.author == None:
                print(f"Skip comment (deleted - no author found): {comment.id} ")
                continue

            print(f"Process comment: {comment.id} {comment.author.name}: {comment.created_utc}, Subcomments: {len(comment.replies)}")
            comment_changed = process_comment(comment, bet, totals)
            changed = changed or comment_changed
    
    print("Update main post")
    body = get_post_text(bet)
    print("old: %s, new: %s" % (len(submission.selftext), len(body)))
    if submission.selftext == body:
        print("No changes -> skip update")
    else:
        print("Update text of post")
        submission.edit(body)
