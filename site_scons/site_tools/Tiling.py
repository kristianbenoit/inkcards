import SCons.Builder

def _tiling_comm_gen(source, target, env, for_signature):
    card_w     = int(int(env['INKCARDS_DENSITY']) * float(env['INKCARDS_GEOM_ATT'][1]))
    card_h     = int(int(env['INKCARDS_DENSITY']) * float(env['INKCARDS_GEOM_ATT'][0]))
    card_cnt_w = int(int(env['INKCARDS_DENSITY']) * float(env['INKCARDS_GEOM_ATT'][3]))
    card_cnt_h = int(int(env['INKCARDS_DENSITY']) * float(env['INKCARDS_GEOM_ATT'][2]))
    env.Replace(INKCARDS_GEOM = '%sx%s+%s+%s'%(card_w, card_h, card_cnt_w, card_cnt_h))
    return env['INKCARDS_TILINGCOMM']

_tiling = SCons.Builder.Builder(
    generator = _tiling_comm_gen,
    suffix = '.pdf',
    src_suffix = '.svg')

def generate(env):
    """Add Builders and construction variables for Inkcards (an Inkscape extension to create cards) to an Environment. The size are relative."""
    env['INKCARDS_DENSITY'] = 300           # Per unit (inches)
    env['INKCARDS_TILE'] = '2x4'            # Cards
    env['INKCARDS_PAGE_SIZE'] = '8.5x11'    # Inches
    env['INKCARDS_ROT'] = 90                # Degree
    env['INKCARDS_GEOM_ATT'] = [2.5,3.5,0.2,0.2] # Inches per cards
    env['INKCARDS_TILINGCOMM'] = 'montage $SOURCES -size $INKCARDS_PAGE_SIZE -geometry $INKCARDS_GEOM -density $INKCARDS_DENSITY -rotate $INKCARDS_ROT -tile $INKCARDS_TILE $TARGET'
    env['BUILDERS']['Tiling'] = _tiling

def exists(env):
    return 1
