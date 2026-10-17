"""Bounded public terminal selection; no sampled identities or chance execution."""
from catanatron.models.enums import ActionType as AT
from race_math import hidden_vp_cap


def public_terminal(g, me, initial_enemy_public, opp_count, unseen_vps):
    ps=g.state.player_state
    k='P'+str(g.state.color_to_index[me])
    enemy=next(c for c in g.state.colors if c!=me)
    ek='P'+str(g.state.color_to_index[enemy])
    if ps[k+'_ACTUAL_VICTORY_POINTS'] < g.vps_to_win:
        return False
    public=ps[ek+'_VICTORY_POINTS']
    # The engine's last qualifying color wins. Real input was nonterminal;
    # unchanged opponent public VP cannot suddenly create a real opponent win.
    return (g.state.colors[-1]==me or public<=initial_enemy_public or
            public+hidden_vp_cap(initial_enemy_public,opp_count,unseen_vps)<g.vps_to_win)


def terminal_action(obs, actions):
    """Certify an immediate legal own win before expensive context/sampling.

    At most 12 road/settlement copies; the fast city/Knight cases need none.
    An incomplete bounded scan returns None, not a claim no win exists.
    The harness's masked game supplies public geometry/own exact cards only.
    """
    g=obs._game
    gap=g.vps_to_win-obs.my_actual_vps
    if gap>3:
        return None
    ps=g.state.player_state;k='P'+str(g.state.color_to_index[obs.me])
    enemy=next(c for c in g.state.colors if c!=obs.me)
    ek='P'+str(g.state.color_to_index[enemy])
    for i,a in enumerate(actions):
        if a.action_type==AT.BUILD_CITY and gap<=1:
            return i
        if a.action_type==AT.PLAY_KNIGHT_CARD and gap<=2:
            count=ps[k+'_PLAYED_KNIGHT']+1
            if not ps[k+'_HAS_ARMY'] and count>=3 and (not ps[ek+'_HAS_ARMY'] or count>ps[ek+'_PLAYED_KNIGHT']):
                return i
    copies=0
    for i,a in enumerate(actions):
        if a.action_type not in (AT.BUILD_SETTLEMENT,AT.BUILD_ROAD):continue
        if a.action_type==AT.BUILD_ROAD and gap>2:continue
        child=g.copy();child.execute(a);copies+=1
        if public_terminal(child,obs.me,obs.opp_public_vps,obs.opp_dev_count,
                           max(0,5-obs.my_devs['VICTORY_POINT'])):
            return i
        if copies>=12:break
    return None
