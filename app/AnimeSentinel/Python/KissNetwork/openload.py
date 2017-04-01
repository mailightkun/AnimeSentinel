#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Code take from plugin IPTVPlayer: "https://gitlab.com/iptvplayer-for-e2/iptvplayer-for-e2/
# Modified for use with Plex Media Server by Twoure (03/21/17)

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
RE_NORM = Regex(r'(https?://\w+\.\w+)/\w+/([^/]+)(/.+)?')

def js2py_decode(hurls, page):
    try:
        page = Regex(r'(\$\(document\).+?\}\})\)\;').search(page).group(1).decode('string_escape')
        code = page.replace("$(document)['ready'](function()", "function getUrl(r)")
        code = Regex(r'\=(\_[^\]]+?\]\(\$.+?r\).*?\[["\']text["\']\][^\)]+?\))').sub('=r', code)
        code = Regex(r'\:\_[^\]]+?\]\(\$.+?["\']\#streamurl["\']\).*?\[["\']text["\']\]\(([^\)]+?\))\)').sub(r':return \1', code)
        code = code.replace("['", '.').replace("']", '').replace('.,', ',').replace('.)', ')')

        context = js2py.EvalJs()
        context.execute(code)
    except:
        Log.Exception("* <openload.js2py_decode[0]> - error: cannot decode with method 03/21/17 >>>")
        return False

    for (hid, k) in hurls:
        if " " in k:
            continue
        try:
            dat = context.getUrl(k)
            return dat
        except:
            Log.Exception("* <openload.js2py_decode[1]> - error: cannot decode with method 03/21/17 >>>")
    return False

def decode_k(k, p0, p1, p2):
    try:
        y = ord(k[0]);
        e = y - p1
        d = max(2, e)
        e = min(d, len(k) - p0 - 2)
        t = k[e:e + p0]
        h = 0
        g = []
        while h < len(t):
            f = t[h:h+3]
            g.append(int(f, 0x8))
            h += 3
        v = k[0:e] + k[e+p0:]
        p = []
        i = 0
        h = 0
        while h < len(v):
            B = v[h:h + 2]
            C = v[h:h + 3]
            D = v[h:h + 4]
            f = int(B, 0x10)
            h += 0x2

            if (i % 3) == 0:
                f = int(C, 8)
                h += 1
            elif i % 2 == 0 and i != 0 and ord(v[i-1]) < 0x3c:
                f = int(D, 0xa)
                h += 2

            A = g[i % p2]
            f = f ^ 0xd5;
            f = f ^ A;
            p.append( chr(f) )
            i += 1
        return "".join(p)
    except:
        Log.Exception("* <openload.decode_k> - error: cannot decode with method 03/20/17 >>>")
    return False

def decode_hiddenUrl(hurls, page):
    tab = [(0x24, 0x37, 0x7), (0x1e, 0x34, 0x6)]
    try:
        page = Regex(r'\$\(document\)(.+?)\}\}\)\;').search(page).group(1).decode('string_escape')
        p0 = Regex(r'splice(.+?)\;').search(page).group(1)
        p0 = Regex(r'\,(0x[0-9a-fA-F]+?)\)').search(p0).group(1)
        p1 = Regex(r'\'#\'(.+?)continue').search(page).group(1)
        p1 = Regex(r'\,(0x[0-9a-fA-F]+?)\)').search(p1).group(1)
        p2 = Regex(r'\^\=0x(.+?)var\s').search(page).group(1)
        p2 = Regex(r'\,(0x[0-9a-fA-F]+?)\)').search(p2).group(1)
        tab.insert(0, (int(p0, 16), int(p1, 16), int(p2, 16)))
    except:
        Log.Exception("* <openload.decode_hiddenUrl> - error: cannot decode with method 03/20/17 >>>")

    for (hid, k) in hurls:
        if " " in k:
            continue
        for item in tab:
            dec = decode_k(k, *item[:3])
            if dec:
                return dec
    return False

def OpenloadStreamFromURL(url, http_headers=None):
    if not http_headers:
        http_headers = {'User-Agnet': USER_AGENT, 'Referer': url}

    base = RE_NORM.search(url)
    eurl = base.group(1) + '/embed/' + base.group(2) + (base.group(3) if base.group(3) else '')

    try:
        page = HTTP.Request(eurl, encoding=('utf-8'), headers=http_headers, cacheTime=CACHE_1MINUTE).content
    except UnicodeDecodeError, ude:
        Log.Warn(u"* Warning: Content removed by Openload for '{0}'".format(eurl))
        Log(str(ude))
        return False
    except:
        Log(u"* Error handling '{0}' >>>".format(eurl))
        Log.Exception(u"* Error: Cannot Open/Decode Openload page >>>")
        return False

    html = HTML.ElementFromString(page)
    hiddenUrls = html.xpath('//span[@id]')
    if hiddenUrls:
        #hurl = decode_hiddenUrl([(h.get('id'), h.text) for h in hiddenUrls], page)
        hurl = js2py_decode([(h.get('id'), h.text) for h in hiddenUrls], page)
        if hurl:
            return u'https://openload.co/stream/{0}?mime=true'.format(hurl)
        else:
            Log.Error(u'* Cannot directly decode hiddenUrl.')
    else:
        Log.Warn(u'* No hiddenUrl to decode.')
    return False