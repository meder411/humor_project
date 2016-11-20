import pysrt

ep = 24
milli = 1436235 + 1399265

filename = 'ep' + str(ep) + '.srt'

subs = pysrt.open(filename)
subs.shift(milliseconds=-milli)
subs.clean_indexes()
subs.save('ep' + str(ep) + '_.srt')
