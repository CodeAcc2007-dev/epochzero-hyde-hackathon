"""Public deterministic win certificates; bounded scans never claim completeness.

Immediate selector adapted from Member3 round-2 terminal_math.py. This independent
Member1 copy adds a bounded one-trade completion before economy-goal filtering.
"""
import time
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
    return (g.state.colors[-1]==me or public<=initial_enemy_public or
            public+hidden_vp_cap(initial_enemy_public,opp_count,unseen_vps)<g.vps_to_win)


def immediate_terminal(g, me, actual, public, count, unseen, actions, limit=12, deadline=None):
    gap=g.vps_to_win-actual
    if gap>3:return None,0,False
    ps=g.state.player_state;k='P'+str(g.state.color_to_index[me])
    enemy=next(c for c in g.state.colors if c!=me);ek='P'+str(g.state.color_to_index[enemy])
    for i,a in enumerate(actions):
        if a.action_type==AT.BUILD_CITY and gap<=1:return i,0,False
        if a.action_type==AT.PLAY_KNIGHT_CARD and gap<=2:
            played=ps[k+'_PLAYED_KNIGHT']+1
            if not ps[k+'_HAS_ARMY'] and played>=3 and (not ps[ek+'_HAS_ARMY'] or played>ps[ek+'_PLAYED_KNIGHT']):
                return i,0,False
    copies=0
    for i,a in enumerate(actions):
        if a.action_type not in (AT.BUILD_SETTLEMENT,AT.BUILD_ROAD):continue
        if a.action_type==AT.BUILD_ROAD and gap>2:continue
        if copies>=limit or (deadline is not None and time.process_time()>=deadline):return None,copies,True
        child=g.copy();child.execute(a);copies+=1
        if public_terminal(child,me,public,count,unseen):return i,copies,False
    return None,copies,False


def terminal_action(obs,actions):
    return immediate_terminal(obs._game,obs.me,obs.my_actual_vps,obs.opp_public_vps,
                              obs.opp_dev_count,max(0,5-obs.my_devs['VICTORY_POINT']),actions)[0]


def terminal_trade(obs,actions,deadline):
    """Only one maritime trade then legal build; <=12 trades, <=48 executions.

    No heuristic trade permission or sampled hidden score participates. Original
    root index is retained. A timeout/cap means unsearched, never impossible.
    """
    g=obs._game;gap=g.vps_to_win-obs.my_actual_vps
    if gap>2:return None,0,False
    k='P'+str(g.state.color_to_index[obs.me]);ps=g.state.player_state
    costs=[]
    if gap<=1:costs.append((0,0,0,2,3))
    # Settlement may transfer Road as well as add its ordinary VP.
    costs.append((1,1,1,1,0))
    if gap<=2 and not ps[k+'_HAS_ROAD'] and ps[k+'_LONGEST_ROAD_LENGTH']>=4:
        costs.append((1,1,0,0,0))
    res=('WOOD','BRICK','SHEEP','WHEAT','ORE')
    h=tuple(ps[k+'_'+r+'_IN_HAND'] for r in res)
    copies=trades=0
    for i,a in enumerate(actions):
        if a.action_type!=AT.MARITIME_TRADE:continue
        after=list(h)
        for r in a.value[:-1]:
            if r is not None:after[res.index(r)]-=1
        after[res.index(a.value[-1])]+=1
        if not any(all(x>=n for x,n in zip(after,cost)) for cost in costs):continue
        if trades>=12 or copies>=48 or time.process_time()>=deadline:return None,copies,True
        child=g.copy();child.execute(a);copies+=1;trades+=1
        completion,n,cut=immediate_terminal(child,obs.me,obs.my_actual_vps,obs.opp_public_vps,
            obs.opp_dev_count,max(0,5-obs.my_devs['VICTORY_POINT']),child.playable_actions,
            limit=min(12,48-copies),deadline=deadline)
        copies+=n
        if completion is not None:return i,copies,cut
        if cut:return None,copies,True
    return None,copies,False
