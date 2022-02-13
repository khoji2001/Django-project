
def persian_numbers_converter(num , mode ='other'):
    under_zero = False
    if num == None:
        num = 0
    if mode == 'price':
        if num<0:
            under_zero = True
            num = -1 * num
    num = str(num)
    numbers = {
           "0" : "۰",
           "1" : "۱",
           "2" : "۲",
           "3" : "۳",
           "4" : "۴",
           "5" : "۵",
           "6" : "۶",
           "7" : "۷",
           "8" : "۸",
           "9" : "۹",
    }
    persian_num = ""
    for i in range(len(num)):
        if ( num[i] in numbers):
            persian_num += numbers[num[i]]
        else:
            persian_num += num[i]
    if (mode == 'price'):
        persian_num = persian_num[::-1]
        if persian_num.count('.') == 0:
            persian_num = ','.join( [ persian_num[i:i+3] for i in range(0,len(persian_num),3) ] )
        else:
            s1,s2 = persian_num.split('.')
            s2 = ','.join( [ s2[i:i+3] for i in range(0,len(s2),3) ] )
            persian_num = s1 + '.' + s2
        if under_zero:
            persian_num += '-'
        return persian_num[::-1]

    else:
        return persian_num

def convert_to_englishnum(num , mode ='other'):
    num = str(num)
    numbers = {
           "۰" : "0",
           "۱" : "1",
           "۲" : "2",
           "۳" : "3",
           "۴" : "4",
           "۵" : "5",
           "۶" : "6",
           "۷" : "7",
           "۸" : "8",
           "۹" : "9",
    }
    english_num = ""
    for i in range(len(num)):
        if ( num[i] in numbers):
            english_num += numbers[num[i]]
        else:
            english_num += num[i]

    if (mode == 'vcc_number'):
        english_num = '-'.join( [ english_num[i:i+4] for i in range(0,len(english_num),4) ] )

    return english_num

## File: num2words/fa.py
##
## Author: Saeed Rasooli <saeed.gnu@gmail.com>    (ilius)
##
## This library is free software; you can redistribute it and/or
## modify it under the terms of the GNU Lesser General Public
## License as published by the Free Software Foundation; either
## version 2.1 of the License, or (at your option) any later version.
##
## This library is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the GNU
## Lesser General Public License for more details.

import sys

faBaseNum = {
    
    1: 'یک',
    2: 'دو',
    3: 'سه',
    4: 'چهار',
    5: 'پنج',
    6: 'شش',
    7: 'هفت',
    8: 'هشت',
    9: 'نه',
    10: 'ده',
    11: 'یازده',
    12: 'دوازده',
    13: 'سیزده',
    14: 'چهارده',
    15: 'پانزده',
    16: 'شانزده',
    17: 'هفده',
    18: 'هجده',
    19: 'نوزده',
    20: 'بیست',
    30: 'سی',
    40: 'چهل',
    50: 'پنجاه',
    60: 'شصت',
    70: 'هفتاد',
    80: 'هشتاد',
    90: 'نود',
    100: 'صد',
    200: 'دویست',
    300: 'سیصد',
    500: 'پانصد'
}
faBaseNumKeys = faBaseNum.keys()
faBigNum = ["یک", "هزار", "میلیون", "میلیارد"]
faBigNumSize = len(faBigNum)


def split3(st):
    parts = []
    n = len(st)
    d, m = divmod(n, 3)
    for i in range(d):
        parts.append(int(st[n - 3 * i - 3:n - 3 * i]))
    if m > 0:
        parts.append(int(st[:m]))
    return parts


def convert(st):
    if isinstance(st,float):
        st = int(st)
    if isinstance(st, int):
        st = str(st)
    elif not isinstance(st, str):
        raise TypeError('bad type "%s"' % type(st))
    if len(st) > 3:
        parts = split3(st)
        k = len(parts)
        wparts = []
        for i in range(k):
            faOrder = ''
            p = parts[i]
            if p == 0:
                continue
            if i == 0:
                wpart = convert(p)
            else:
                if i < faBigNumSize:
                    faOrder = faBigNum[i]
                else:
                    faOrder = ''
                    (d, m) = divmod(i, 3)
                    t9 = faBigNum[3]
                    for j in range(d):
                        if j > 0:
                            faOrder += "‌"
                        faOrder += t9
                    if m != 0:
                        if faOrder != '':
                            faOrder = "‌" + faOrder
                        faOrder = faBigNum[m] + faOrder
                wpart = faOrder if i == 1 and p == 1 else convert(p) + " " + faOrder
            wparts.append(wpart)
        return " و ".join(reversed(wparts))
    ## now assume that n <= 999
    n = int(st)
    if n in faBaseNumKeys:
        return faBaseNum[n]
    y = n % 10
    d = int((n % 100) / 10)
    s = int(n / 100)

    dy = 10 * d + y
    fa = ''
    if s != 0:
        if s * 100 in faBaseNumKeys:
            fa += faBaseNum[s * 100]
        else:
            fa += (faBaseNum[s] + faBaseNum[100])
        if d != 0 or y != 0:
            fa += ' و '
    if d != 0:
        if dy in faBaseNumKeys:
            fa += faBaseNum[dy]
            return fa
        fa += faBaseNum[d * 10]
        if y != 0:
            fa += ' و '
    if y != 0:
        fa += faBaseNum[y]
    return fa


def convert_ordinary(arg):
    if isinstance(arg, int):
        num = arg
        st = str(arg)
    elif isinstance(arg, str):
        num = int(arg)
        st = arg
    else:
        raise TypeError('bad type "%s"' % type(arg))
    if num == 1:
        return 'اول'  ## OR 'یکم' ## FIXME
    elif num == 10:
        return 'دهم'
    norm_fa = convert(st)#.encode('utf-8')
    if len(norm_fa) == 0:
        return ''
    if norm_fa.endswith(u'ی'):
        norm_fa += u'‌ام'
    elif norm_fa.endswith(u'سه'):
        norm_fa = norm_fa[:-1] + u'وم'
    else:
        norm_fa += u'م'
    return norm_fa#.encode('utf-8')
