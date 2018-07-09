import SCons.Builder

# To create the cards whenever inkcards.conf is changed.
# I was tryed to set INKCARDSCONF through the builder creation with no luck YET.

def _inkcards_add_conf(target, source, env):
    env.Replace(INKCARDSCONF = env.File('inkcards.conf'))
    source += [env.File(env['INKCARDSCONF'])]
    return target, source

_inkcards = SCons.Builder.Builder(
    action = "./cards.py --tab=show --card=$CARD_NB --side=$CARD_SIDE --file=$INKCARDSCONF -- $SOURCE > $TARGET",
    suffix = '.svg',
    src_suffix = '.svg',
    emitter = _inkcards_add_conf)

def generate(env):
    env['BUILDERS']['Inkcards'] = _inkcards

def exists(env):
    return 1
