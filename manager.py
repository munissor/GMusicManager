#!/usr/bin/env python
# -*- coding: utf-8 -*-

from operator import itemgetter
from getpass import getpass

from gmusicapi import Mobileclient

def normalize_songs(songs):
    for s in songs:
        if not s.has_key('playCount'):
            s['playCount'] = 0
        if not s.has_key('year'):
            s['year'] = 9999
        if not s.has_key('rating'):
            s['rating'] = -1

def process_playlist(api, allsongs, songs, playlists, target):
    
    playlist = None
        
    for x in playlists:
        if x['name'] == target:
            playlist = x
            break
            
    playlistEntries = playlist['tracks']
        
    toRemove = []
    toAdd = []
    
    for pe in playlistEntries:
        songinfo =  [s for s in songs if s['id'] == pe['trackId']]
        if len(songinfo) == 0:
            t = [tx for tx in allsongs if tx['id'] == pe['trackId']]
            if len(t) > 0:
                print 'Marking song for removal: ' + t[0]['artist'] + ' - ' + t[0]['title']
            else:
                print 'Marking song for removal: ' + pe['trackId'] 
            toRemove.append(pe['id'])
                
    for s in songs:
        entries = [e for e in playlistEntries if e['trackId'] == s['id'] ]
        if len(entries) == 0:
            print 'Marking song for addition: ' + s['artist'] + ' - ' + s['title']
            toAdd.append(s['id']) 
    
    newentries = len(songs) - len(playlistEntries) + len(toRemove)
    if len(toAdd) > newentries:
        toAdd = toAdd[:newentries]
    
    
    if len(toRemove) > 0:
        print 'Removing entries...'
        api.remove_entries_from_playlist(toRemove)

    if len(toAdd) > 0:
        print 'Adding entries...'
        api.add_songs_to_playlist(playlist['id'], toAdd)

def process_playlists():
   
    # We're not going to upload anything, so the Mobileclient is what we want.
    api = Mobileclient()
   
    logged_in = False
    attempts = 0

    while not logged_in and attempts < 3:
        email = raw_input('Email: ')
        password = getpass()

        logged_in = api.login(email, password)
        attempts += 1

    if not api.is_authenticated():
        print "Sorry, those credentials weren't accepted."
        return
    
   
    print 'Successfully logged in.'
    print
    
    print 'Loading library...',        
    allsongs = api.get_all_songs()
    normalize_songs(allsongs)
    
    print 'Loading playlists...'    
    playlists = api.get_all_user_playlist_contents()
    
    maxentries = 1000
    
    ## NOT STARRED
    # TOP N entries sorted by playCount
    print 'Processing Discovery...'    
    discoverysongs = sorted(allsongs, key=itemgetter('playCount', 'artist', 'year', 'title'))
    if len(discoverysongs) > maxentries:
        discoverysongs = discoverysongs[:maxentries]
    
    process_playlist(api, allsongs, discoverysongs, playlists, 'Discovery')
    
    # STARRED
    print 'Processing Starred...'   
    starredsongs = [s for s in allsongs if s['rating'] == '5']
    starredsongs = sorted(starredsongs, key=itemgetter('playCount', 'artist', 'year', 'title'))
    
    if len(starredsongs) > maxentries:
        starredsongs = starredsongs[:maxentries]
        
    process_playlist(api, allsongs, starredsongs, playlists, 'Starred')
    
    # It's good practice to logout when finished.
    api.logout()
    print 'All done!'
    return

    

if __name__ == '__main__':
    process_playlists()
