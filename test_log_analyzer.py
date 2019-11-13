
import unittest
from log_analyzer import *


lines = [
'1.196.116.32 -  - [29/Jun/2017:03:52:44 +0300] "GET /api/v2/banner/22911507 HTTP/1.1" 200 590 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697564-2190034393-4708-9754322" "dc7161be3" 0.071',
'1.196.116.32 -  - [29/Jun/2017:03:52:44 +0300] "GET /api/v2/banner/20825304 HTTP/1.1" 200 739 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697564-2190034393-4708-9754318" "dc7161be3" 0.073',
'1.196.116.32 -  - [29/Jun/2017:03:52:44 +0300] "GET /api/v2/banner/22913947 HTTP/1.1" 200 576 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697564-2190034393-4708-9754324" "dc7161be3" 0.074',
'1.196.116.32 -  - [29/Jun/2017:03:52:44 +0300] "GET /api/v2/banner/20828125 HTTP/1.1" 200 739 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697564-2190034393-4708-9754319" "dc7161be3" 0.075'
]



#def get_lines(lines):
#    for line in lines:
#        yield(line)

#p = parse_line(lines)
#print(p.__next__())


class LogAnalyzerTest(unittest.TestCase):
    def test_mediana(self):
        self.assertEqual(mediana([1, 2, 3]), 2, "Should be 2")
        self.assertEqual(mediana([1, 2, 3, 4]), 2.5)

    def test_r2(self):
        self.assertEqual(r2( 1  ), 1.0)
        self.assertEqual(r2(1.111111111), 1.111  )

    def test_parse_line(self):
        p = parse_line(lines)
        self.assertEqual(p.__next__(), ('GET /api/v2/banner/22911507 HTTP/1.1', '0.071'))
        self.assertEqual(p.__next__(), ('GET /api/v2/banner/20825304 HTTP/1.1', '0.073'))
        self.assertEqual(p.__next__(), ('GET /api/v2/banner/22913947 HTTP/1.1', '0.074'))
        self.assertEqual(p.__next__(), ('GET /api/v2/banner/20828125 HTTP/1.1', '0.075'))
#        self.assertIsNone(p.__next__())


if __name__ == '__main__':
    unittest.main()
