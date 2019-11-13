
import unittest
from log_analyzer import *


lines_diff = [
'1.196.116.32 -  - [29/Jun/2017:03:52:44 +0300] "GET /api/v2/banner/22911507 HTTP/1.1" 200 590 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697564-2190034393-4708-9754322" "dc7161be3" 0.061',
'1.196.116.32 -  - [29/Jun/2017:03:52:44 +0300] "GET /api/v2/banner/20825304 HTTP/1.1" 200 739 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697564-2190034393-4708-9754318" "dc7161be3" 0.063',
'1.196.116.32 -  - [29/Jun/2017:03:52:44 +0300] "GET /api/v2/banner/22913947 HTTP/1.1" 200 576 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697564-2190034393-4708-9754324" "dc7161be3" 0.065',
]

lines_equal = [
'1.196.116.32 -  - [29/Jun/2017:03:52:44 +0300] "GET /api/v2/banner/HTTP/1.1" 200 590 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697564-2190034393-4708-9754322" "dc7161be3" 0.061',
'1.196.116.32 -  - [29/Jun/2017:03:52:44 +0300] "GET /api/v2/banner/HTTP/1.1" 200 739 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697564-2190034393-4708-9754318" "dc7161be3" 0.063',
'1.196.116.32 -  - [29/Jun/2017:03:52:44 +0300] "GET /api/v2/banner/HTTP/1.1" 200 576 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697564-2190034393-4708-9754324" "dc7161be3" 0.065',
]

lines_both = [
'1.196.116.32 -  - [29/Jun/2017:03:52:44 +0300] "GET /api/v2/banner/1/HTTP/1.1" 200 590 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697564-2190034393-4708-9754322" "dc7161be3" 0.061',
'1.196.116.32 -  - [29/Jun/2017:03:52:44 +0300] "GET /api/v2/banner/2/HTTP/1.1" 200 739 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697564-2190034393-4708-9754318" "dc7161be3" 0.063',
'1.196.116.32 -  - [29/Jun/2017:03:52:44 +0300] "GET /api/v2/banner/2/HTTP/1.1" 200 576 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697564-2190034393-4708-9754324" "dc7161be3" 0.065',
]

#def get_lines(lines):
#    for line in lines:
#        yield(line)

#p = parse_line(lines)
#print(p.__next__())


class LogAnalyzerTest(unittest.TestCase):
    def test_mediana(self):
        self.assertEqual(mediana([1, 2, 3]), 2)
        self.assertEqual(mediana([1, 2, 3, 4]), 2.5)

    def test_r2(self):
        self.assertEqual(r2( 1  ), 1.0)
        self.assertEqual(r2(1.111111111), 1.111  )

    def test_parse_line(self):
        #test lines parsing
        p = parse_line(lines_diff)
        self.assertEqual(p.__next__(), ('GET /api/v2/banner/22911507 HTTP/1.1', '0.061'))
        self.assertEqual(p.__next__(), ('GET /api/v2/banner/20825304 HTTP/1.1', '0.063'))
        self.assertEqual(p.__next__(), ('GET /api/v2/banner/22913947 HTTP/1.1', '0.065'))
        self.assertRaises(StopIteration, p.__next__)

    def test_get_statistics(self):
        dicted_diff = get_statistics(parse_line(lines_diff))
        self.assertEqual(dicted_diff.__next__(), ({'GET /api/v2/banner/22911507 HTTP/1.1': [1, 0.061, 0.061, 0.061, 1, [0.061]], 'GET /api/v2/banner/20825304 HTTP/1.1': [1, 0.063, 0.063, 0.063, 2, [0.063]],
                                              'GET /api/v2/banner/22913947 HTTP/1.1': [1, 0.065, 0.065, 0.065, 3, [0.065]]}, 0.189))
        dicted_equal = get_statistics(parse_line(lines_equal))
        self.assertEqual(dicted_equal.__next__(), ({'GET /api/v2/banner/HTTP/1.1': [3, 0.063, 0.065, 0.189, 3, [0.061, 0.063, 0.065]]}, 0.189))
        dicted_both = get_statistics(parse_line(lines_both))
        self.assertEqual(dicted_both.__next__(), ({'GET /api/v2/banner/1/HTTP/1.1': [1, 0.061, 0.061, 0.061, 1, [0.061]], 'GET /api/v2/banner/2/HTTP/1.1': [2, 0.064, 0.065, 0.128, 3, [0.063, 0.065]]}, 0.189))

    def test_handle_dict(self):
        handled_diff=handle_dict({'GET /api/v2/banner/22911507 HTTP/1.1': [1, 0.061, 0.061, 0.061, 1, [0.061]], 'GET /api/v2/banner/20825304 HTTP/1.1': [1, 0.063, 0.063, 0.063, 2, [0.063]],
                         'GET /api/v2/banner/22913947 HTTP/1.1': [1, 0.065, 0.065, 0.065, 3, [0.065]]}, 0.189, 0)
        handled_equal=handle_dict({'GET /api/v2/banner/HTTP/1.1': [3, 0.063, 0.065, 0.189, 3, [0.061, 0.063, 0.065]]}, 0.189, 0)
        handled_both = handle_dict({'GET /api/v2/banner/1/HTTP/1.1': [1, 0.061, 0.061, 0.061, 1, [0.061]], 'GET /api/v2/banner/2/HTTP/1.1': [2, 0.064, 0.065, 0.128, 3, [0.063, 0.065]]}, 0.189, 0)
        self.assertEqual(len(handled_diff), 3)
        self.assertEqual(len(handled_equal), 1)
        self.assertEqual(len(handled_both), 2)

    def test_handle_dict_report_size(self):
        handled_more = handle_dict({'GET /api/v2/banner/1/HTTP/1.1': [1, 0.061, 0.061, 0.061, 1, [0.061]], 'GET /api/v2/banner/2/HTTP/1.1': [2, 0.064, 0.065, 0.128, 3, [0.063, 0.065]]}, 0.189, 1)
        handled_more_and_less = handle_dict({'GET /api/v2/banner/1/HTTP/1.1': [1, 0.061, 0.061, 0.061, 1, [0.061]], 'GET /api/v2/banner/2/HTTP/1.1': [2, 0.064, 0.065, 0.128, 3, [0.063, 0.065]]}, 0.189, 0.062)
        self.assertEqual(len(handled_more), 0)
        self.assertEqual(len(handled_more_and_less), 1)


if __name__ == '__main__':
    unittest.main()
