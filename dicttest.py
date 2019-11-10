
d = dict()
#print(d)
#print(type(d))
from collections import OrderedDict
d = {'GET /export/appinstall_raw/2017-06-30/ HTTP/1.0' : ['0.001', 1]}

dn = {'GET /api/v2/internal/banner/24061825/info HTTP/1.1': ['0.081', 1]}

d.update(dn)

#print(type(d))


st = 'al/banner/24061'
st2 = 'GET /api/v2/internal/banner/24061825/info HTTP/1.1'
#print(d['GET /api/v2/internal/banner/24061825/info HTTP/1.1'])
#print(d[st])

#print(d.get(st))

nevvalue = ('0.5')
payload = d.get(st2)

newpayload = [payload[1] + float(nevvalue), payload[1] + 1]

#print(d)
d[st2] = newpayload

#print(d)

for i in d.keys():
#    print(d[i])
    pay = d[i]
    pay[1] = 30
    d[i] = pay

#print(d.values())


print(d)


res = []
for i,j in d.items():
    print(i)
    print(j)
    res.append([i, *j])

print(res)



res =[['GET /api/v2/banner/25019354 HTTP/1.1', 1, 0.0, 0.39, 0.39, 0.0, 1.0, 0.39, 1], ['GET /api/1/photogenic_banners/list/?server_name=WIN7RB4 HTTP/1.1', 5, 0.0, 0.04, 0.14, 0.0, 0.0, 0.14, 4175]]


h= sorted(res, key= lambda x : x[6])

print(h)



