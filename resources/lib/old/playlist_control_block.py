# separate order and value
plabel = 32410
vlabel = 32130

choices_label = 32130
choices2_label = 32140
enum_label = 32190
enum2_label = 32480
choices = (   ( "feature_presentation_intro", "Feature presentation intro", ),
                    ( "slideshow_intro", "Slideshow intro", ),
                    ( "coming_attractions_intro", "Coming attractions intro", ),
                    ( "information_clips", "Information clip(s)", ),
                    ( "commercial_clips", "Commercial clip(s)", ),
                    ( "intermission_clips", "Intermission clip(s)", ),
                    ( "other_clips", "Other clip(s)", ) )

choices2 = ( "- File", "- Folder", )

enums2 = (   "None",
                    "Execute command",
                    "Feature presentation",
                    "Slideshow",
                    "Movie trailer(s)",
                    "MPAA rating",
                    "Dolby/DTS video",
                    choices[ 0 ][ 1 ],
                    choices[ 1 ][ 1 ],
                    choices[ 2 ][ 1 ],
                    choices[ 3 ][ 1 ],
                    choices[ 4 ][ 1 ],
                    choices[ 5 ][ 1 ],
                    choices[ 6 ][ 1 ], )

enums = (   "Single video/image",
                    "1 Random video/image",
                    "2 Random videos/images",
                    "3 Random videos/images",
                    "4 Random videos/images",
                    "5 Random videos/images", )

svideos_control_block = """    <setting label="%d" type="enum" id="%s" default="0" lvalues="%s" />
    <setting label="%d" type="files" id="%s_file" default="" source="auto" visible="eq(-1,0)" />
    <setting label="%d" type="folder" id="%s_folder" default="" source="auto" visible="gt(-2,0)" />"""

playlist_control_block = "    <setting label=\"%d\" type=\"enum\" id=\"playlist_item%d\" default=\"0\" lvalues=\"%s\" />"

for count in range( len( choices ) ):
    print "    <string id=\"%d\">%s</string>" % ( choices_label + count, choices[ count ][ 1 ], )
print
for count in range( len( choices2 ) ):
    print "    <string id=\"%d\">%s</string>" % ( choices2_label + count, choices2[ count ], )
print
for count in range( len( enums ) ):
    print "    <string id=\"%d\">%s</string>" % ( enum_label + count, enums[ count ], )
print
for count in range( 12 ):
    print "    <string id=\"%d\">Item #%d</string>" % ( plabel + count, count + 1, )
print
for count in range( len( enums2 ) ):
    print "    <string id=\"%d\">%s</string>" % ( enum2_label + count, enums2[ count ], )
print

for count in range( len( choices ) ):
    print svideos_control_block % ( choices_label + count, choices[ count ][ 0 ], "|".join( [ str( v ) for v in range( enum_label, enum_label + len( enums ) ) ] ), choices2_label, choices[ count ][ 0 ], choices2_label + 1, choices[ count ][ 0 ], )
print

for count in range( 12 ):
    print playlist_control_block % ( plabel + count, count + 1, "|".join( [ str( v ) for v in range( enum2_label, enum2_label + len( enums2 ) ) ] ) )
print


"""

# order with category selection instead of file/folder selection
sId = 32140
plabel = 32101
for count in range( 1, 13 ):
    print playlist_control_block3 % ( count, "".join( [ "|%s" % ( i + sId, ) for i in range( len( choices3 ) * 6 ) ] ), plabel + count - 1 )
print
for choice in choices3:
    print choices_string_block3 % ( sId, choice, sId + 1, choice, sId + 2, choice, sId + 3, choice, sId + 4, choice, sId + 5, choice, )
    sId += 6
print
print "-"*70
print

# combined order and value
plabel = 32101
for count in range( 1, 13 ):
    print playlist_control_block2 % ( count, plabel + count - 1, count, -1, 32118, count, -2, 32119, )
print
print choices_string_block1
print
print "-"*70
print

# separate order and value
controlOffset = -13
vlabel = 32601
for count in range( 1, 13 ):
    print playlist_control_block1 % ( count, plabel + count - 1, )
print
for count in range( 1, 13 ):
    print pvalues_control_block1 % ( count, controlOffset, vlabel, count, controlOffset - 1, vlabel + 1, controlOffset - 2, vlabel +2, )
    controlOffset -= 2
    vlabel += 3
print
print choices_string_block1
print
print "-"*70
print

"""