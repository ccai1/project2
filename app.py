import os
import sqlite3

from flask import Flask, render_template, request, session, redirect, url_for, flash
from passlib.hash import sha256_crypt

import db_edit
from util import routes, transit, music

app = Flask(__name__)
app.secret_key = os.urandom(8)

@app.route('/')
def home():
    ''' this function loads up home session, from where user can login and navigate through the website'''
    #checks if there is a session
    if 'user' in session:
        #if there is then just show the welcome screen
        return render_template('welcome.html',
                                user=session['user'])
    else:
        #if not just ask for info
        return render_template('home.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    '''logs the user in by checking if their login info matches with registered user'''
    username = request.form['usr'].strip()
    password = request.form['pwd'].strip()
    user_exists = db_edit.findInfo('users', db_edit.checkApos(username), 'username', fetchOne = True)
    '''find password for username'''
    if user_exists:
        # print (user_exists)
        # print (password)
        # print (sha256_crypt.verify(password, user_exists[2]))
        if sha256_crypt.verify(password, user_exists[2]):
            session['user'] = username
            return redirect(url_for('home'))
        else:
            flash("Wrong password!")
            return render_template('home.html')
    flash("Wrong username!")
    return redirect(url_for('home'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    '''registers new account for user'''
    password = request.form['new_pwd'].strip()
    username= request.form['new_usr'].strip()
    pwdCopy = request.form['re_pwd'].strip()
    if username.find("'") == -1:
            if password == pwdCopy:
                # db_edit.insert('users', [username, sha256_crypt.encrypt(password), ""])
                try:
                    db_edit.insert('users', [username, '', sha256_crypt.encrypt(password)])
                    '''insert username and password into database'''
                    flash("Registration complete! Please re-enter your login info.");
                except:
                    flash("That username is taken. Please use a different one.");
            else:
                flash('Passwords do not match.')
    else:
        flash("Pick a username without apostrophes")
    return redirect(url_for('home'))

@app.route('/route', methods=['POST', 'GET'])
def route():
    start = request.form['start'].strip()
    destination = request.form['destination'].strip()
    mode = request.form['mode']

    top_hit = music.get_top_tracks(1)
    print ('---TOP HIT---')
    print (top_hit)

    if start and destination:
        info = routes.getDirectionsInfo(start, destination, "shortest")
        map = routes.get_maps(info)
        distance = routes.get_distance(info)

    # add driving to this
        if mode == "Walking" or mode == "Driving" or mode == "Bicycle":
            '''runs the route.py algorithm'''

            '''ROUTE DIRECTIONS'''

            if mode == "Walking":
                try:
                    info = routes.getDirectionsInfo(start, destination, "pedestrian")
                    route = routes.get_directions(info)
                except:
                    flash("You can't walk that far! Please select a different transportation type.")
                    return redirect(url_for('home'))

            elif mode == "Bicycle":
                info = routes.getDirectionsInfo(start, destination, "bicycle")
            else:
                info = routes.getDirectionsInfo(start, destination, "driving")

            route = routes.get_directions(info)
            time = routes.get_time(info)
            hour = str(time // 3600)
            minute = str((time % 3600) // 60)
            second = str(time % 60)
            if hour == '0':
                hour = ""
            elif hour == '1':
                hour += " hour "
            else:
                hour += " hours "

            if minute == '0':
                minute = ""
            elif minute == '1':
                minute += " minute and "
            else:
                minute += " minutes and "

            if second == '0':
                second = ""
                minute.replace(" and ", "")
            elif second == '1':
                second += " second "
            else:
                second += " seconds "

            time = hour + minute + second

            # print ("-----ROUTE INFO-----")
            # print (info)

        else:

            '''TRANSIT DIRECTIONS'''

            info = transit.get_transit_info(start, destination)
            route = []

            for i in range (0, len(info)):

                #per route found
                one_route = {}

                time = transit.get_total_time(info[i])
                directions = transit.get_directions(info[i])
                one_route['time'] = time
                one_route['directions'] = directions
                route.append(one_route)

        # print ("----TRANSIT ROUTES----")
        # print (route)

        return render_template('route.html',
                                mode=mode,
                                time=time,
                                distance=distance,
                                map=map,
                                routes=route,
                                top_hit = top_hit)
    else:
        flash("Please fill in all address forms.")
        return redirect(url_for('home'))


@app.route('/play', methods=['POST', 'GET'])
def play():
    '''runs the song algorithm'''

    tags = request.form.get('tags')
    artist = request.form.get('artist')

    transit_time = request.form.get('route')
    route_time = request.form.get('time')


    print ('---PLAY IS CALLED---')
    print (time)
    playlist = music.gen_playlist(time, tags)
    return render_template('play.html',
                            playlist = playlist
    )

# Consider: Do we need an edit page?
#
@app.route('/edit', methods=['POST', 'GET'])
def edit():
    '''displays the playlist with options to delete, select, and shuffle'''
    # playlist = request.form['playlist']
    # getting songs and to display
    # return render_template('edit.html')
    return redirect(url_for('play'))

@app.route('/logout')
def logout():
    '''pops user from session, brings user back to home page'''
    session.pop('user')
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
