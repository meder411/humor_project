import pysrt

ep = 24

milli = 1369235+1377243

filename = 'ep' + str(ep) + '.srt'

subs = pysrt.open(filename)
subs.shift(milliseconds=-milli)
subs.clean_indexes()
subs.save('ep' + str(ep) + '_.srt')
