
try:
    watched = []
    file_object = open( r"F:\source\_XBMC_\userdata\script_data\Home Theater Experience\loca1l_watched.txt", "r" )
    watched = eval( file_object.read() )
    file_object.close()
except Exception, e:
    # oops, notify user what error occurred
    print "*** %s" % ( e, )
print watched