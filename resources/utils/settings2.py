setting = """        <setting label="$ADDON[script.cinema.experience 30410] #%d" type="select" id="playlist_item%d" default="$ADDON[script.cinema.experience 30411]" lvalues="30411|30412|30413|30414|30415|30416|30417|30418|30419"%s/>
        <setting label="30350" subsetting="true" type="audio" id="playlist_item%d_music_playlist" default="" source="auto" visible="StringCompare(Addon.Setting(playlist_item%d),$ADDON[script.cinema.experience 30418]) + [Control.HasFocus(%d) | Control.HasFocus(%d)]"/>
        <setting label="30430" subsetting="true" type="enum" id="playlist_item%d_number" default="1" lvalues="30431|30432|30433|30434|30435|30436|30437" visible="StringCompare(Addon.Setting(playlist_item%d),$ADDON[script.cinema.experience 30413]) + [Control.HasFocus(%d) | Control.HasFocus(%d) | Control.HasFocus(%d) | Control.HasFocus(%d) | Control.HasFocus(%d)]"/>
        <setting label="30440" subsetting="true" type="file" id="playlist_item%d_file" default="" source="auto" mask="$IMAGE|$VIDEO" visible="!IntegerGreaterThan(Addon.Setting(playlist_item%d_number),0) + Control.IsVisible(%d)"/>
        <setting label="30450" subsetting="true" type="folder" id="playlist_item%d_folder" default="" source="auto" visible="IntegerGreaterThan(Addon.Setting(playlist_item%d_number),0) + Control.IsVisible(%d)"/>
        <setting label="30460" subsetting="true" type="slider" id="playlist_item%d_duration" default="10" range="5,1,60" format="%%1.f $ADDON[script.cinema.experience 30461]" visible="Control.IsVisible(%d)"/>
        <setting type="sep" visible="Control.IsVisible(%d) | Control.IsVisible(%d)"/>"""

visible = 201
status = ""
status2 = 1
visible2 = 201
#       <setting label="$ADDON[script.cinema.experience 30410] #2" type="select" id="playlist_item2" default="$ADDON[script.cinema.experience 30411]" lvalues="30411|30412|30413|30414|30415|30416|30417|30418|30419" visible="!Control.IsVisible(202) + !Control.IsVisible(203)" allowhiddenfocus="true"/>
 
for control in range( 1, 16 ):
    print setting % ( control, control, status, control, control, visible, visible + 1, control, control, visible, visible + 2, visible + 3, visible + 4, visible + 5, control, control, visible + 2, control, control, visible + 2, control, visible + 2, visible + 1, visible + 2 )
    """
        <setting label="$ADDON[script.cinema.experience 30410] #1" type="select" id="playlist_item1" default="$ADDON[script.cinema.experience 30411]" lvalues="30411|30412|30413|30414|30415|30416|30417|30418|30419"/>
        <setting label="30350" subsetting="true" type="audio" id="playlist_item1_music_playlist" default="" source="auto" visible="StringCompare(Addon.Setting(playlist_item1),$ADDON[script.cinema.experience 30418]) + [Control.HasFocus(201) | Control.HasFocus(202)]"/>
        <setting label="30430" subsetting="true" type="enum" id="playlist_item1_number" default="1" lvalues="30431|30432|30433|30434|30435|30436|30437" visible="StringCompare(Addon.Setting(playlist_item1),$ADDON[script.cinema.experience 30413]) + [Control.HasFocus(201) | Control.HasFocus(203) | Control.HasFocus(204) | Control.HasFocus(205) | Control.HasFocus(206)]"/>
        <setting label="30440" subsetting="true" type="file" id="playlist_item1_file" default="" source="auto" mask="$IMAGE|$VIDEO" visible="!IntegerGreaterThan(Addon.Setting(playlist_item1_number),0) + Control.IsVisible(203)"/>
        <setting label="30450" subsetting="true" type="folder" id="playlist_item1_folder" default="" source="auto" visible="IntegerGreaterThan(Addon.Setting(playlist_item1_number),0) + Control.IsVisible(203)"/>
        <setting label="30460" subsetting="true" type="slider" id="playlist_item1_duration" default="10" range="5,1,60" format="%1.f $ADDON[script.cinema.experience 30461]" visible="Control.IsVisible(203)"/>
        <setting type="sep" visible="Control.IsVisible(202) | Control.IsVisible(203)"/>
        <setting label="$ADDON[script.cinema.experience 30410] #2" type="select" id="playlist_item2" default="$ADDON[script.cinema.experience 30411]" lvalues="30411|30412|30413|30414|30415|30416|30417|30418|30419" visible="!Control.IsVisible(202) + !Control.IsVisible(203)" allowhiddenfocus="true"/>
        <setting label="30350" subsetting="true" type="audio" id="playlist_item2_music_playlist" default="" source="auto" visible="StringCompare(Addon.Setting(playlist_item2),$ADDON[script.cinema.experience 30418]) + [Control.HasFocus(208) | Control.HasFocus(209)]"/>
        <setting label="30430" subsetting="true" type="enum" id="playlist_item2_number" default="1" lvalues="30431|30432|30433|30434|30435|30436|30437" visible="StringCompare(Addon.Setting(playlist_item2),$ADDON[script.cinema.experience 30413]) + [Control.HasFocus(208) | Control.HasFocus(210) | Control.HasFocus(211) | Control.HasFocus(212) | Control.HasFocus(213)]"/>
        <setting label="30440" subsetting="true" type="file" id="playlist_item2_file" default="" source="auto" mask="$IMAGE|$VIDEO" visible="!IntegerGreaterThan(Addon.Setting(playlist_item2_number),0) + Control.IsVisible(210)"/>
        <setting label="30450" subsetting="true" type="folder" id="playlist_item2_folder" default="" source="auto" visible="IntegerGreaterThan(Addon.Setting(playlist_item2_number),0) + Control.IsVisible(210)"/>
        <setting label="30460" subsetting="true" type="slider" id="playlist_item2_duration" default="10" range="5,1,60" format="%1.f $ADDON[script.cinema.experience 30461]" visible="Control.IsVisible(210)"/>
        <setting type="sep" visible="Control.IsVisible(209) | Control.IsVisible(210)"/>
        <setting label="$ADDON[script.cinema.experience 30410] #3" type="select" id="playlist_item3" default="$ADDON[script.cinema.experience 30411]" lvalues="30411|30412|30413|30414|30415|30416|30417|30418|30419" visible="!Control.IsVisible(209) + !Control.IsVisible(203) + !Control.IsVisible(210)" allowhiddenfocus="true"/>
        <setting label="30350" subsetting="true" type="audio" id="playlist_item3_music_playlist" default="" source="auto" visible="StringCompare(Addon.Setting(playlist_item3),$ADDON[script.cinema.experience 30418]) + [Control.HasFocus(215) | Control.HasFocus(216)]"/>
        <setting label="30430" subsetting="true" type="enum" id="playlist_item3_number" default="1" lvalues="30431|30432|30433|30434|30435|30436|30437" visible="StringCompare(Addon.Setting(playlist_item3),$ADDON[script.cinema.experience 30413]) + [Control.HasFocus(215) | Control.HasFocus(217) | Control.HasFocus(218) | Control.HasFocus(219) | Control.HasFocus(220)]"/>
        <setting label="30440" subsetting="true" type="file" id="playlist_item3_file" default="" source="auto" mask="$IMAGE|$VIDEO" visible="!IntegerGreaterThan(Addon.Setting(playlist_item3_number),0) + Control.IsVisible(217)"/>
        <setting label="30450" subsetting="true" type="folder" id="playlist_item3_folder" default="" source="auto" visible="IntegerGreaterThan(Addon.Setting(playlist_item3_number),0) + Control.IsVisible(217)"/>
        <setting label="30460" subsetting="true" type="slider" id="playlist_item3_duration" default="10" range="5,1,60" format="%1.f $ADDON[script.cinema.experience 30461]" visible="Control.IsVisible(217)"/>
        <setting type="sep" visible="Control.IsVisible(216) | Control.IsVisible(217)"/>
"""
    status = " visible=\"!Control.IsVisible(%d) + %s\" allowhiddenfocus=\"true\"" % ( visible2 + (status2-1)*7 + 1, " + ".join( [ "!Control.IsVisible(%d)" % ( visible2 + i*7 + 2, ) for i in range( status2 ) ] ), )
    visible += 7
    if ( status2 < 3 ):
        status2 += 1
    else:
        visible2 += 7

    #print status