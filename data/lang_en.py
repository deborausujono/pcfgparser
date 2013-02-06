import re

PTAG_S     = 'S'
PTAG_SBAR  = 'SBAR'

PTAG_CONJP = 'CONJP'
PTAG_INTJ  = 'INTJ'
PTAG_NP    = 'NP'
PTAG_PP    = 'PP'
PTAG_PRN   = 'PRN'
PTAG_UCP   = 'UCP'
PTAG_VP    = 'VP'
PTAG_WHNP  = 'WHNP'
PTAG_WHPP  = 'WHPP'

PTAG_CC    = 'CC'
PTAG_COMMA = ','
PTAG_COLON = ':'

FTAG_ETC   = 'ETC'
FTAG_PRD   = 'PRD'
FTAG_SBJ   = 'SBJ'

RE_COMP_POS  = re.compile('^(WDT|WP.*|WRB)$')
RE_COMP_ANTE = re.compile('^(WHNP|WHPP)$')
RE_COMP_FORM = re.compile('^(how|however|that|what|whatever|whatsoever|when|whenever|where|whereby|wherein|whereupon|wherever|which|whichever|whither|who|whoever|whom|whose|why)$')


