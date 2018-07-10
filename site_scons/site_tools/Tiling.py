import SCons.Builder

def _tiling_emitter(target, source, env):
    #env.Replace(TILE = env['page_layout'])
    source = [i for i in source if not (str(i)).endswith(str(env['INKCARDSCONF']))]
    return target, source

_tiling = SCons.Builder.Builder(
    #action = "../cards.py --tab=show --card=$CARD_NB --side=$CARD_SIDE --file=$INKCARDSCONF -- $SOURCE > $TARGET",
    action = 'montage $SOURCES -rotate 90 -density $DPI -tile 2x3 $TARGET',
    suffix = '.pdf',
    src_suffix = '.svg',
    emitter = _tiling_emitter)

def generate(env):
    env['BUILDERS']['Tiling'] = _tiling

def exists(env):
    return 1
