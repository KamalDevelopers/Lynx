import confvar
from abp.filters import parse_filterlist
from adblockparser import AdblockRules

adblock_url_rules = None
adblock_css_rules = None
adblock_url_max = 2000
adblock_css_max = 1000


def stripRule(rule):
    rule = rule.replace("//*", "").replace("^", "").replace("*", "").replace("$", "")
    return rule


def readFilter(path, regen=False):
    global adblock_url_rules
    global adblock_css_rules

    url_rules = []
    css_rules = []
    block = " { display: none !important; visibility: hidden !important; } "

    with open(path) as filterlist:
        for line in parse_filterlist(filterlist):
            if line.type == "filter":
                if line.selector['type'] == "url-pattern" and len(url_rules) < adblock_url_max:
                    url_rules.append(line.text)
                if line.selector['type'] == "url-regexp" and len(url_rules) < adblock_url_max:
                    url_rules.append(line.text)
                if line.selector['type'] == "css" and len(css_rules) < adblock_css_max:
                    if line.text[:2] == "##":
                        css_rules.append(stripRule(line.text.split("##")[1]))

    url_rules.append("tpc.googlesyndication.com/*")
    adblock_url_rules = AdblockRules(url_rules)
    adblock_css_rules = ','.join(css_rules) + block

    with open(confvar.BASE_PATH + "adblock/generated.css", "w") as F:
        F.write(adblock_css_rules)


def match(url):
    global adblock_url_rules
    if not adblock_url_rules:
        return False
    return adblock_url_rules.should_block(url)
