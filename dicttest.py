
d = dict()
print(d)
print(type(d))

d = {'GET /export/appinstall_raw/2017-06-30/ HTTP/1.0' : ('0.001', 1)}

dn = {'GET /api/v2/internal/banner/24061825/info HTTP/1.1': ('0.081', 1)}

d.update(dn)

print(type(d))


st = 'al/banner/24061'
st2 = 'GET /api/v2/internal/banner/24061825/info HTTP/1.1'
#print(d['GET /api/v2/internal/banner/24061825/info HTTP/1.1'])
#print(d[st])

print(d.get(st))

nevvalue = ('0.5')
payload = d.get(st2)

newpayload = (payload[1] + float(nevvalue), payload[1] + 1)

print(d)
d[st2] = newpayload

print(d)