import SCons.Builder

def _inkcards_add_conf(target, source, env):
    """Add INKCARDSCONF to the source so the cards are rebuilt it's changed"""
    env.SetDefault(INKCARDSCONF = env.File('inkcards.conf'))
    source += [env.File(env['INKCARDSCONF'])]
    return target, source

_inkcards = SCons.Builder.Builder(
    action = "./cards.py --tab=show --card=$CARD_NB --side=$CARD_SIDE --file=$INKCARDSCONF --svgout=$TARGET -- $SOURCE",
    suffix = '.svg',
    src_suffix = '.svg',
    emitter = _inkcards_add_conf)

def generate(env):
    env['BUILDERS']['Inkcards'] = _inkcards

def exists(env):
    return 1
